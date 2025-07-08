from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
import json
import uuid
import base64
from server.redis_client import redis_client

app = FastAPI()

@app.get("/debug/tunnels")
def get_active_tunnels():
    all_keys = redis_client.keys("tunnel:*")
    tunnels = [key.split(":", 1)[1] for key in all_keys]
    return {"active_tunnels": tunnels}


@app.api_route("/{tunnel}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(tunnel: str, path: str, request: Request):
    print(f"📡 Request to tunnel: {tunnel}, path: {path}")

    if not redis_client.exists(f"tunnel:{tunnel}"):
        return JSONResponse(content={"error": "Tunnel not found"}, status_code=404)

    body = await request.body()
    response_queue = f"response_queue:{tunnel}:{uuid.uuid4()}"

    payload = {
        "type": "http_request",
        "method": request.method,
        "path": f"/{path}",
        "headers": dict(request.headers),
        "body": body.decode(errors="ignore") if body else "",
        "response_queue": response_queue
    }

    redis_client.rpush(f"request_queue:{tunnel}", json.dumps(payload).encode())

    response_raw = redis_client.blpop(response_queue, timeout=10)
    if not response_raw or not response_raw[1]:
        return JSONResponse(content={"error": "No response from client"}, status_code=504)

    try:
        response_data = json.loads(response_raw[1])
    except Exception as e:
        print(f"[PARSING ERROR] ❌ Could not parse response: {e}")
        return JSONResponse(
            content={"error": "Invalid response format", "raw": response_raw[1].decode(errors="ignore")},
            status_code=502
        )

    status_code = response_data.get("status_code", 200)
    headers = response_data.get("headers", {})

    if "body" in response_data:
        return Response(
            content=response_data["body"],
            status_code=status_code,
            headers=headers
        )
    elif "raw_base64" in response_data:
        decoded = base64.b64decode(response_data["raw_base64"])
        return Response(
            content=decoded,
            status_code=status_code,
            headers=headers
        )
    else:
        return JSONResponse(content={"detail": "Empty response"}, status_code=status_code)
