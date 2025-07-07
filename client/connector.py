import socket
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", 9999))

def connect_to_server(tunnel_name):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_HOST, SERVER_PORT))
        print(f"[CLIENT] ✅ Connected to server at {SERVER_HOST}:{SERVER_PORT}")

        registration_msg = f"REGISTER:{tunnel_name}"
        sock.sendall(registration_msg.encode())
        print(f"[CLIENT] 🛰️ Sent registration: {registration_msg}")

        return sock
    except Exception as e:
        print(f"[CLIENT] ❌ Connection error: {e}")
        return None
