import json
import os
import time
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key

# --- Environment & AWS clients ---
PARTS_TABLE_NAME = os.environ["PARTS_TABLE"]
BOM_TABLE_NAME = os.environ["BOM_TABLE"]

dynamodb = boto3.resource("dynamodb")
parts_tbl = dynamodb.Table(PARTS_TABLE_NAME)
bom_tbl = dynamodb.Table(BOM_TABLE_NAME)
ddb_client = boto3.client("dynamodb")

# --- CORS & utils ---
CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PATCH,PUT,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
}

def _now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _to_jsonable(x):
    if isinstance(x, Decimal):
        f = float(x)
        return int(f) if f.is_integer() else f
    if isinstance(x, list):
        return [_to_jsonable(v) for v in x]
    if isinstance(x, dict):
        return {k: _to_jsonable(v) for k, v in x.items()}
    return x

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps(_to_jsonable(body)),
    }

def _require_fields(obj, fields):
    for f in fields:
        if f not in obj:
            raise ValueError(f"Missing field '{f}'")

def _parse_int(val, name):
    try:
        return int(val)
    except Exception:
        raise ValueError(f"Field '{name}' must be an integer")

# --- Handlers ---

def handle_get_parts(query):
    # NOTE: DynamoDB cannot filter "quantity < min_quantity" server-side (attr-to-attr),
    # so we scan and compute below_min in code. Fine for small tables; can optimize later.
    scan = parts_tbl.scan()
    items = scan.get("Items", [])
    below_min_flag = (query.get("below_min", "false").lower() == "true")
    out = []
    for it in items:
        q = it.get("quantity", 0)
        m = it.get("min_quantity", 0)
        it["below_min"] = q < m
        if below_min_flag and not it["below_min"]:
            continue
        out.append(it)
    return _resp(200, out)

def handle_post_parts(body):
    _require_fields(body, ["code", "name"])
    code = str(body["code"])
    name = str(body["name"])
    quantity = _parse_int(body.get("quantity", 0), "quantity")
    min_quantity = _parse_int(body.get("min_quantity", 0), "min_quantity")

    item = {
        "code": code,
        "name": name,
        "quantity": quantity,
        "min_quantity": min_quantity,
        "updated_at": _now_iso(),
    }
    try:
        parts_tbl.put_item(Item=item, ConditionExpression="attribute_not_exists(code)")
    except Exception as e:
        return _resp(409, {"error": "Part already exists", "detail": str(e)})
    return _resp(201, item)

def handle_patch_part(code, body):
    has_delta = "quantity_delta" in body
    has_set_q = "quantity" in body
    has_min = "min_quantity" in body
    if not (has_delta or has_set_q or has_min):
        return _resp(400, {"error": "Provide quantity_delta and/or quantity and/or min_quantity"})

    expr_vals = {":now": _now_iso(), ":zero": Decimal(0)}
    updates = ["updated_at = :now"]

    if has_delta:
        dq = _parse_int(body["quantity_delta"], "quantity_delta")
        expr_vals[":dq"] = Decimal(dq)
        updates.append("quantity = if_not_exists(quantity, :zero) + :dq")

    if has_set_q:
        q = _parse_int(body["quantity"], "quantity")
        expr_vals[":q"] = Decimal(q)
        updates.append("quantity = :q")

    if has_min:
        mq = _parse_int(body["min_quantity"], "min_quantity")
        expr_vals[":mq"] = Decimal(mq)
        updates.append("min_quantity = :mq")

    try:
        res = parts_tbl.update_item(
            Key={"code": code},
            UpdateExpression="SET " + ", ".join(updates),
            ExpressionAttributeValues=expr_vals,
            ConditionExpression="attribute_exists(code)",
            ReturnValues="ALL_NEW",
        )
    except Exception as e:
        return _resp(404, {"error": f"Part '{code}' not found", "detail": str(e)})

    item = res.get("Attributes", {})
    q = item.get("quantity", 0)
    m = item.get("min_quantity", 0)
    item["below_min"] = q < m
    return _resp(200, item)

def handle_put_bom(parent_code, body):
    """
    Body: [{ "component_code": "SCREW-10MM", "units_per_parent": 8 }, ...]
    Strategy: replace the BOM for parent_code (delete existing, insert new).
    """
    if not isinstance(body, list) or not body:
        return _resp(400, {"error": "Body must be a non-empty array of components"})

    # Validate
    cleaned = []
    for comp in body:
        try:
            _require_fields(comp, ["component_code", "units_per_parent"])
            cc = str(comp["component_code"])
            up = _parse_int(comp["units_per_parent"], "units_per_parent")
            if up <= 0:
                return _resp(400, {"error": "units_per_parent must be > 0"})
            cleaned.append({"parent_code": parent_code, "component_code": cc, "units_per_parent": up})
        except ValueError as ve:
            return _resp(400, {"error": str(ve)})

    # Delete existing BOM rows
    existing = bom_tbl.query(KeyConditionExpression=Key("parent_code").eq(parent_code)).get("Items", [])
    with bom_tbl.batch_writer() as bw:
        for it in existing:
            bw.delete_item(Key={"parent_code": it["parent_code"], "component_code": it["component_code"]})
        for it in cleaned:
            bw.put_item(Item=it)

    return _resp(200, {"ok": True, "parent_code": parent_code, "count": len(cleaned)})

def handle_get_bom(parent_code):
    res = bom_tbl.query(KeyConditionExpression=Key("parent_code").eq(parent_code))
    items = res.get("Items", [])
    return _resp(200, items)

def handle_build(parent_code, body):
    """
    Body: { "quantity": N }
    Atomically:
      - Increment parent quantity by N
      - Decrement each component quantity by (N * units_per_parent)
      - Prevent negative stock (ConditionExpression)
    Limit: max 25 operations per transaction (1 parent + up to 24 components)
    """
    try:
        _require_fields(body, ["quantity"])
        build_qty = _parse_int(body["quantity"], "quantity")
        if build_qty <= 0:
            return _resp(400, {"error": "quantity must be > 0"})
    except ValueError as ve:
        return _resp(400, {"error": str(ve)})

    # Load BOM components
    bom_items = bom_tbl.query(KeyConditionExpression=Key("parent_code").eq(parent_code)).get("Items", [])
    if not bom_items:
        return _resp(400, {"error": f"No BOM defined for {parent_code}"})

    if len(bom_items) + 1 > 25:
        return _resp(400, {"error": "BOM too large for a single transaction (max 24 components). Consider chunking via Step Functions."})

    # Pre-read components to construct nice error if stock is insufficient
    components = []
    for comp in bom_items:
        comp_code = comp["component_code"]
        units = int(comp["units_per_parent"])
        need = build_qty * units
        # read part
        pr = parts_tbl.get_item(Key={"code": comp_code})
        part = pr.get("Item")
        have = part.get("quantity", 0) if part else None
        components.append({"component_code": comp_code, "units_per_parent": units, "need": need, "have": have})

    missing = []
    for c in components:
        if c["have"] is None or c["have"] < c["need"]:
            missing.append({"component_code": c["component_code"], "need": c["need"], "have": (c["have"] if c["have"] is not None else 0)})
    if missing:
        return _resp(409, {"error": "INSUFFICIENT_STOCK", "parent_code": parent_code, "missing": missing})

    # Build transact write items
    actions = []

    # Parent increment
    actions.append({
        "Update": {
            "TableName": PARTS_TABLE_NAME,
            "Key": {"code": {"S": parent_code}},
            "UpdateExpression": "SET quantity = if_not_exists(quantity, :z) + :inc, updated_at = :now",
            "ExpressionAttributeValues": {
                ":z":   {"N": "0"},
                ":inc": {"N": str(build_qty)},
                ":now": {"S": _now_iso()},
            },
            "ConditionExpression": "attribute_exists(code)"
        }
    })

    # Components decrement with stock guard
    for c in components:
        actions.append({
            "Update": {
                "TableName": PARTS_TABLE_NAME,
                "Key": {"code": {"S": c["component_code"]}},
                "UpdateExpression": "SET quantity = quantity - :need, updated_at = :now",
                "ExpressionAttributeValues": {
                    ":need": {"N": str(c["need"])},
                    ":now":  {"S": _now_iso()},
                },
                "ConditionExpression": "attribute_exists(code) AND quantity >= :need"
            }
        })

    try:
        ddb_client.transact_write_items(TransactItems=actions)
    except Exception as e:
        # In case of race, return generic conflict
        return _resp(409, {"error": "TRANSACTION_FAILED", "detail": str(e)})

    # Return updated parent snapshot
    parent = parts_tbl.get_item(Key={"code": parent_code}).get("Item", {"code": parent_code})
    parent["updated_at"] = _now_iso()
    return _resp(200, {"ok": True, "parent": parent})

# --- Main dispatcher ---

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("rawPath", "")
    query = event.get("queryStringParameters") or {}
    path_params = event.get("pathParameters") or {}
    body = {}
    if event.get("body"):
        try:
            body = json.loads(event["body"])
        except Exception:
            return _resp(400, {"error": "Invalid JSON body"})

    # CORS preflight
    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    # Health
    if method == "GET" and path == "/health":
        return _resp(200, {
            "ok": True,
            "time": _now_iso(),
            "env": {"PARTS_TABLE": PARTS_TABLE_NAME, "BOM_TABLE": BOM_TABLE_NAME}
        })

    # Parts
    if method == "GET" and path == "/parts":
        return handle_get_parts(query)

    if method == "POST" and path == "/parts":
        try:
            return handle_post_parts(body)
        except ValueError as ve:
            return _resp(400, {"error": str(ve)})

    if method == "PATCH" and path_params.get("code") and path.startswith("/parts/"):
        return handle_patch_part(path_params["code"], body)

    # BOM
    if method == "PUT" and path_params.get("parent_code") and path.startswith("/bom/"):
        return handle_put_bom(path_params["parent_code"], body)

    if method == "GET" and path_params.get("parent_code") and path.startswith("/bom/"):
        return handle_get_bom(path_params["parent_code"])

    # Build (assemblies)
    if method == "POST" and path_params.get("parent_code") and path.startswith("/assemblies/") and path.endswith("/build"):
        return handle_build(path_params["parent_code"], body)

    return _resp(404, {"error": f"No route for {method} {path}"})
