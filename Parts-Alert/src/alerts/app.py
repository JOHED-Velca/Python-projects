import os
import time
import json
from decimal import Decimal

import boto3

PARTS_TABLE = os.environ["PARTS_TABLE"]
ALERTS_STATE_TABLE = os.environ["ALERTS_STATE_TABLE"]
ALERTS_TOPIC_ARN = os.environ["ALERTS_TOPIC_ARN"]

ddb = boto3.resource("dynamodb")
parts_tbl = ddb.Table(PARTS_TABLE)
state_tbl = ddb.Table(ALERTS_STATE_TABLE)
sns = boto3.client("sns")

def _now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _to_py(x):
    if isinstance(x, Decimal):
        f = float(x)
        return int(f) if f.is_integer() else f
    if isinstance(x, dict):
        return {k: _to_py(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_to_py(v) for v in x]
    return x

def _read_all_parts():
    items = []
    scan_kwargs = {}
    while True:
        resp = parts_tbl.scan(**scan_kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            break
        scan_kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    return items

def lambda_handler(event, context):
    # 1) Gather low-stock items
    parts = _read_all_parts()
    low = []
    for it in parts:
        q = it.get("quantity", 0)
        m = it.get("min_quantity", 0)
        try:
            # ensure ints
            q = int(q)
            m = int(m)
        except Exception:
            pass
        if q < m:
            low.append(it)

    # Sort to get a stable "signature"
    low_codes = sorted([p["code"] for p in low if "code" in p])
    signature = ",".join(low_codes)

    # 2) Load last signature from state table
    state_key = {"pk": "low_stock"}
    res = state_tbl.get_item(Key=state_key)
    last_sig = (res.get("Item") or {}).get("signature", "")

    # 3) If nothing changed, exit quietly
    if signature == last_sig:
        return {"ok": True, "changed": False, "count": len(low)}

    # 4) If changed and there are low items, publish SNS
    if low:
        # Build a human-friendly message
        lines = [
            f"Low-stock items as of {_now_iso()} ({len(low)} items):",
            ""
        ]
        for p in low:
            code = p.get("code", "?")
            name = p.get("name", "")
            qty = p.get("quantity", 0)
            minq = p.get("min_quantity", 0)
            lines.append(f"- {code:15} {name:30} qty={qty}  min={minq}")
        msg = "\n".join(lines)

        sns.publish(
            TopicArn=ALERTS_TOPIC_ARN,
            Subject="Low Stock Alert",
            Message=msg
        )

    # 5) Update signature (even if empty -> clears previous alert state)
    state_tbl.put_item(Item={
        "pk": "low_stock",
        "signature": signature,
        "updated_at": _now_iso()
    })

    return {"ok": True, "changed": True, "count": len(low)}
