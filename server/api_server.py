from fastapi import FastAPI, Request
from fastapi.responses import Response
import json
from server.redis_client import redis_client

app = FastAPI()

@app.get("/debug/tunnels")
def get_active_tunnels():
    return {"active_tunnels": list(redis_client.keys())}

@app.api_route("/{tunnel}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(tunnel: str, path: str, request: Request):
    print(f"Received request for tunnel: {tunnel}, path: {path}")
    if not redis_client.get(f"tunnel:{tunnel}"):
        return Response(content=json.dumps({"error": "Tunnel not found"}), status_code=404, media_type="application/json")

    body = await request.body()
    payload = {
        "type": "http_request",
        "method": request.method,
        "path": f"/{path}",
        "headers": dict(request.headers),
        "body": body.decode() if body else None
    }

    try:
        client_sock = redis_client.get(f"tunnel:{tunnel}")
        client_sock.sendall(json.dumps(payload).encode())


        response_raw = client_sock.recv(4096)
        response_data = json.loads(response_raw.decode())

        return Response(
            content=response_data.get("body", ""),
            status_code=response_data.get("status_code", 200),
            headers=response_data.get("headers", {})
        )
    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=500, media_type="application/json")