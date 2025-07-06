import socket
import threading
from server.redis_client import redis_client

HOST = '0.0.0.0'
PORT = 9999

def handle_client(client_socket, addr):
    print(f"[SERVER] 🔌 New connection from {addr}")
    try:
        data = client_socket.recv(1024).decode()
        if data.startswith("REGISTER:"):
            tunnel_name = data.split(":", 1)[1]
            redis_client.set(f"tunnel:{tunnel_name}", "active")
            print(f"[SERVER] ✅ Registered tunnel: '{tunnel_name}'")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        pass

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"[SERVER] 🚀 MyTunnel server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()
