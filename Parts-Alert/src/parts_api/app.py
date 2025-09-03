import json
import os
from datetime import datetime, timezone

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PATCH,PUT,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
}

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps(body),
    }

def lambda_handler(event, context):
    # Minimal sanity endpoint for now
    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    if path == "/health":
        return _resp(200, {
            "ok": True,
            "time": datetime.now(timezone.utc).isoformat(),
            "env": {
                "PARTS_TABLE": os.environ.get("PARTS_TABLE"),
                "BOM_TABLE": os.environ.get("BOM_TABLE"),
            }
        })

    # Placeholder until we implement /parts, /bom, /assemblies
    return _resp(404, {"error": f"No route for {method} {path}"})

