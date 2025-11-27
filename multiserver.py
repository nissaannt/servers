import socket
import threading
import time
import sys

# Stores clients for each server (key = server_port)
servers = {}

# Stores the peer socket (inter-server communication)
peer_socket = {
    40000: None,   # for server 1
    45000: None    # for server 2
}

###############################################################
#   BROADCAST TO CLIENTS + FORWARD TO PEER
###############################################################

def broadcast(server_port, msg, sender_username):
    # Send to local clients
    for username, client_socket in list(servers[server_port].items()):
        if username != sender_username:
            try:
                client_socket.send(msg.encode())
            except:
                pass

    # Forward to peer server
    if peer_socket[server_port]:
        try:
            peer_socket[server_port].send(("FWD:" + msg).encode())
        except:
            pass


###############################################################
#   HANDLE PEER MESSAGES
###############################################################

def receive_from_peer(server_port):
    conn = peer_socket[server_port]
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            msg = data.decode()

            # If message forwarded from peer
            if msg.startswith("FWD:"):
                msg = msg[4:]  # remove prefix

                # broadcast ONLY locally
                for username, client_socket in list(servers[server_port].items()):
                    try:
                        client_socket.send(msg.encode())
                    except:
                        pass

        except:
            break

    print(f"[Server {server_port}] Peer disconnected")


###############################################################
#   ACCEPT PEER CONNECTION
###############################################################

def peer_listener(server_port, my_peer_port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("localhost", my_peer_port))
    listener.listen(1)
    print(f"[Server {server_port}] Listening for peer on port {my_peer_port}")

    conn, addr = listener.accept()
    peer_socket[server_port] = conn
    print(f"[Server {server_port}] Peer connected from {addr}")

    threading.Thread(target=receive_from_peer,
                     args=(server_port,), daemon=True).start()


###############################################################
#   CONNECT TO PEER SERVER
###############################################################

def connect_to_peer(server_port, peer_peer_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            s.connect(("localhost", peer_peer_port))
            peer_socket[server_port] = s
            print(f"[Server {server_port}] Connected TO peer at port {peer_peer_port}")

            threading.Thread(target=receive_from_peer,
                             args=(server_port,), daemon=True).start()
            break

        except:
            time.sleep(1)  # retry until peer is ready


###############################################################
#   HANDLE CLIENT
###############################################################

def handle_client(c_socket, c_addr, port):
    username = c_socket.recv(1024).decode().strip()

    if username in servers[port]:
        c_socket.send("Username Taken!".encode())
        c_socket.close()
        return

    servers[port][username] = c_socket
    c_socket.send("OK".encode())
    print(f"[Server {port}]: {username} joined")

    # Notify everyone
    join_msg = f"*** {username} joined the chat ***"
    broadcast(port, join_msg, sender_username=None)

    # Receive messages
    while True:
        try:
            msg = c_socket.recv(1024)
            if not msg:
                break
            msg = msg.decode()

            full_msg = f"{username}: {msg}"
            broadcast(port, full_msg, sender_username=username)

        except:
            break

    # On disconnect
    c_socket.close()
    print(f"[Server {port}]: {username} disconnected")

    if username in servers[port]:
        del servers[port][username]

    leave_msg = f"*** {username} left the chat ***"
    broadcast(port, leave_msg, sender_username=None)


###############################################################
#   START SERVER
###############################################################

def start_server(port, my_peer_port, peer_peer_port):
    servers[port] = {}
    peer_socket[port] = None

    # Start peer listener (to accept the other server)
    threading.Thread(target=peer_listener,
                     args=(port, my_peer_port), daemon=True).start()

    # Start connection attempt to peer
    threading.Thread(target=connect_to_peer,
                     args=(port, peer_peer_port), daemon=True).start()

    # Start client listener
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', port))
    server.listen()

    print(f"[Server {port}] Ready for clients...")

    while True:
        client_socket, client_addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(client_socket, client_addr, port),
            daemon=True
        ).start()


###############################################################
#   MAIN (Two-server execution)
###############################################################

def main():
    if len(sys.argv) != 2:
        print("Usage: python server.py <server_id>")
        print("server_id = 1 or 2")
        return

    sid = int(sys.argv[1])

    if sid == 1:
        # Server 1: client port 40000, peer listen 40100, peer connect to 45100
        start_server(40000, 40100, 45100)

    elif sid == 2:
        # Server 2: client port 45000, peer listen 45100, peer connect to 40100
        start_server(45000, 45100, 40100)

    else:
        print("server_id must be 1 or 2")


main()
