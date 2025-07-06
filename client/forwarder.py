import requests
import json
import os

LOCAL_PORT = int(os.getenv("LOCAL_PORT", 8000))

def handle_forwarding(sock):
    while True:
        try:
            data = sock.recv(65536)
            request = json.loads(data.decode())


            if request.get("type") == "http_request":
                url = f"http://localhost:{LOCAL_PORT}{request['path']}"
                method = request['method'].lower()
                headers = request.get('headers', {})
                body = request.get('body', '')


                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=body
                )
                response_data = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text
                }
                sock.sendall(json.dumps(response_data).encode())
        except Exception as e:
            print(f"[FORWARDER] ❌ Error in forwarding: {e}")
            break