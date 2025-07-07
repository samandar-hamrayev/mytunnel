import requests
import json


def handle_forwarding(sock, local_host, local_port):
    print(f"[FORWARDER] 🔄 Forwarding requests to http://{local_host}:{local_port}")

    while True:
        try:
            data = sock.recv(65536)
            request = json.loads(data.decode())

            if request.get("type") == "http_request":
                url = f"http://{local_host}:{local_port}{request['path']}"
                method = request['method'].lower()
                headers = request.get('headers', {})
                body = request.get('body', '')

                print(f"[FORWARDER] 📤 Sending {method.upper()} request to {url}")

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
