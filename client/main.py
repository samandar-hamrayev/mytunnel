from connector import connect_to_server
from forwarder import handle_forwarding


if __name__ == "__main__":
    sock = connect_to_server()
    if sock:
        print("[CLIENT] 🛰️ Connection established. Starting request forwarding...")
        handle_forwarding(sock)
    else:
        print("[CLIENT] ❌ Failed to connect to the server. Exiting...")