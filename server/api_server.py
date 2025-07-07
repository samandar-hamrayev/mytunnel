# server/api_server.py
from fastapi import FastAPI, Request
from fastapi.responses import Response
import json
import uuid
from server.redis_client import redis_client

app = FastAPI()

@app.get("/debug/tunnels")
def get_active_tunnels():
    all_keys = redis_client.keys("tunnel:*")
    tunnels = [key.split(":", 1)[1] for key in all_keys]
    return {"active_tunnels": tunnels}

@app.api_route("/{tunnel}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(tunnel: str, path: str, request: Request):
    print(f"📡 Request to tunnel: {tunnel}, path: {path}")

    if not redis_client.exists(f"tunnel:{tunnel}"):
        return Response(content=json.dumps({"error": "Tunnel not found"}), status_code=404, media_type="application/json")

    body = await request.body()
    response_queue = f"response_queue:{tunnel}:{uuid.uuid4()}"

    payload = {
        "type": "http_request",
        "method": request.method,
        "path": f"/{path}",
        "headers": dict(request.headers),
        "body": body.decode() if body else None,
        "response_queue": response_queue
    }

    # Send to Redis
    redis_client.rpush(f"request_queue:{tunnel}", json.dumps(payload).encode())

    # Wait for response
    response_raw = redis_client.blpop(response_queue, timeout=10)
    if not response_raw:
        return Response(content=json.dumps({"error": "Timeout"}), status_code=504, media_type="application/json")

    response_data = json.loads(response_raw[1])

    return Response(
        content=response_data.get("body", ""),
        status_code=response_data.get("status_code", 200),
        headers=response_data.get("headers", {})
    )
