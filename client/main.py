import socket
import json
import requests
from server.redis_client import redis_client

TUNNEL_NAME = "samandar"
SERVER_HOST = "localhost"
SERVER_PORT = 9999
LOCAL_SERVER = "http://localhost:8000"

def register():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    sock.sendall(f"REGISTER:{TUNNEL_NAME}".encode())
    return sock

def listen_to_redis():
    queue_name = f"request_queue:{TUNNEL_NAME}"
    print(f"[CLIENT] 🎧 Listening on Redis queue: {queue_name}")

    while True:
        _, request_raw = redis_client.blpop(queue_name)
        request_data = json.loads(request_raw)
        path = request_data["path"]
        method = request_data["method"]
        headers = request_data["headers"]
        body = request_data["body"]
        response_queue = request_data["response_queue"]

        try:
            url = f"{LOCAL_SERVER}{path}"
            print(f"[CLIENT] ⬇️ Forwarding to local: {url}")

            resp = requests.request(method, url, headers=headers, data=body)

            response_data = {
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "body": resp.text,
            }

        except Exception as e:
            response_data = {
                "status_code": 500,
                "headers": {},
                "body": str(e),
            }

        redis_client.rpush(response_queue, json.dumps(response_data))

def main():
    register()
    print("[CLIENT] ✅ Registered with server")
    listen_to_redis()

if __name__ == "__main__":
    main()
