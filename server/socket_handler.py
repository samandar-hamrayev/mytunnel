# server/socket_handler.py
import socket
import threading
import json
import uuid
from server.redis_client import redis_client

HOST = '0.0.0.0'
PORT = 9999

def listen_to_redis(tunnel_name, client_sock):
    queue_name = f"request_queue:{tunnel_name}"
    print(f"[TUNNEL] 🎧 Listening on Redis queue: {queue_name}")
    
    while True:
        _, request_raw = redis_client.blpop(queue_name)
        if not request_raw:
            continue

        try:
            # ❗️request_raw bu str bo'lsa, decode() chaqirilmaydi
            if isinstance(request_raw, bytes):
                request_raw = request_raw.decode()

            payload = json.loads(request_raw)
            response_queue = payload["response_queue"]

            # Clientga yuboramiz
            client_sock.sendall(json.dumps(payload).encode())

            # Clientdan javob kutamiz
            response_raw = client_sock.recv(4096)

            # Redisga response yozamiz (agar redis decode_responses=False bo‘lsa bytes)
            redis_client.rpush(response_queue, response_raw.decode())

        except Exception as e:
            print(f"[ERROR] Tunnel '{tunnel_name}' failed: {e}")
            break

def handle_client(client_socket, addr):
    print(f"[SERVER] 🔌 New connection from {addr}")
    try:
        data = client_socket.recv(1024).decode()
        if data.startswith("REGISTER:"):
            tunnel_name = data.split(":", 1)[1]
            redis_client.set(f"tunnel:{tunnel_name}", b"active")
            print(f"[SERVER] ✅ Registered tunnel: '{tunnel_name}'")

            threading.Thread(target=listen_to_redis, args=(tunnel_name, client_socket), daemon=True).start()
    except Exception as e:
        print(f"[ERROR] {e}")

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"[SERVER] 🚀 MyTunnel socket server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = s.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
