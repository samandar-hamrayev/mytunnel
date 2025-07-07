import argparse
import os
from dotenv import load_dotenv

from client.connector import connect_to_server
from client.forwarder import handle_forwarding

load_dotenv()

def run_client():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tunnel", help="Tunnel name (default from .env)")
    parser.add_argument("--host", help="Local server host (default from .env)")
    parser.add_argument("--port", type=int, help="Local server port (default from .env)")
    args = parser.parse_args()

    tunnel_name = args.tunnel or os.getenv("DEFAULT_TUNNEL_NAME", "samandar")
    local_host = args.host or os.getenv("LOCAL_HOST", "localhost")
    local_port = args.port or int(os.getenv("LOCAL_PORT", 8000))

    sock = connect_to_server(tunnel_name)
    if sock:
        print(f"[CLIENT] ✅ Registered with server as '{tunnel_name}'")
        handle_forwarding(sock, local_host, local_port)
    else:
        print("[CLIENT] ❌ Failed to connect to server.")

if __name__ == "__main__":
    run_client()
