import socket
import threading
import sys

class ChatServer:
    def __init__(self, port, peer_port):
        self.port = port
        self.peer_port = peer_port
        self.clients = []  # Now stores (protocol, socket, addr, username)
        self.clients_lock = threading.Lock()
        
    def start(self):
        # TCP socket
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(('localhost', self.port))
        self.tcp_socket.listen(5)
        
        # UDP socket  
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(('localhost', self.port))
        
        print(f"Server started on port {self.port}")
        print(f"Peer server port: {self.peer_port}")
        
        # Connect to peer server
        self.connect_to_peer()
        
        # Start threads
        threading.Thread(target=self.accept_tcp, daemon=True).start()
        threading.Thread(target=self.handle_udp, daemon=True).start()
        
        try:
            while True:
                input()  # Keep main thread alive
        except KeyboardInterrupt:
            print("Shutting down server...")
    
    def connect_to_peer(self):
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.peer_socket.connect(('localhost', self.peer_port))
            print(f"Connected to peer server on port {self.peer_port}")
            threading.Thread(target=self.receive_from_peer, daemon=True).start()
        except:
            print(f"Failed to connect to peer server on port {self.peer_port}")
    
    def accept_tcp(self):
        while True:
            client_socket, addr = self.tcp_socket.accept()
            print(f"TCP client connected: {addr}, waiting for username...")
            threading.Thread(target=self.handle_tcp_client, args=(client_socket, addr), daemon=True).start()
    
    def handle_udp(self):
        while True:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                if not data:
                    continue
                    
                message = data.decode()
                
                # Check if this is a new UDP client (username registration)
                client_exists = False
                with self.clients_lock:
                    for protocol, sock, client_addr, username in self.clients:
                        if addr == client_addr:
                            client_exists = True
                            break
                
                if not client_exists:
                    # First message from UDP client is their username
                    username = message
                    with self.clients_lock:
                        self.clients.append(('UDP', self.udp_socket, addr, username))
                    print(f"UDP client '{username}' connected: {addr}")
                    
                    # Send confirmation
                    self.udp_socket.sendto("USERNAME_ACCEPTED".encode(), addr)
                    
                    # Notify others
                    join_msg = f"*** {username} joined the chat ***"
                    self.broadcast(join_msg, addr)
                    self.forward_to_peer(join_msg)
                    continue
                
                # Get username for this address
                username = self.get_username(addr)
                formatted_msg = f"{username}: {message}"
                
                # Broadcast to other clients
                self.broadcast(formatted_msg, addr)
                
                # Forward to peer server
                self.forward_to_peer(formatted_msg)
                
            except Exception as e:
                # Ignore UDP connection errors as UDP is connectionless
                if "10054" not in str(e):
                    print(f"UDP error: {e}")
    
    def handle_tcp_client(self, client_socket, addr):
        username = None
        try:
            # First, receive username
            data = client_socket.recv(1024)
            if not data:
                return
            username = data.decode().strip()
            
            # Add client to list
            with self.clients_lock:
                self.clients.append(('TCP', client_socket, addr, username))
            print(f"TCP client '{username}' registered: {addr}")
            
            # Send confirmation
            client_socket.sendall("USERNAME_ACCEPTED".encode())
            
            # Notify others
            join_msg = f"*** {username} joined the chat ***"
            self.broadcast(join_msg, addr)
            self.forward_to_peer(join_msg)
            
            # Handle messages
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode()
                formatted_msg = f"{username}: {message}"
                self.broadcast(formatted_msg, addr)
                self.forward_to_peer(formatted_msg)
        except:
            pass
        finally:
            if username:
                with self.clients_lock:
                    self.clients = [c for c in self.clients if c[2] != addr]
                
                # Notify others
                leave_msg = f"*** {username} left the chat ***"
                self.broadcast(leave_msg, None)
                self.forward_to_peer(leave_msg)
                print(f"TCP client '{username}' disconnected: {addr}")
            
            client_socket.close()
    
    def receive_from_peer(self):
        while True:
            try:
                data = self.peer_socket.recv(1024)
                if not data:
                    break
                self.broadcast(f"[Peer] {data.decode()}", None)
            except:
                break
    
    def get_username(self, addr):
        with self.clients_lock:
            for protocol, sock, client_addr, username in self.clients:
                if client_addr == addr:
                    return username
        return "Unknown"
    
    def broadcast(self, message, exclude_addr):
        with self.clients_lock:
            for protocol, sock, addr, username in self.clients[:]:  # Use slice to avoid modification during iteration
                if addr == exclude_addr:
                    continue
                try:
                    if protocol == 'TCP':
                        sock.sendall(message.encode())
                    else:
                        # For UDP, use the same UDP socket but send to specific address
                        sock.sendto(message.encode(), addr)
                except:
                    # Remove client if sending fails
                    try:
                        self.clients.remove((protocol, sock, addr, username))
                    except:
                        pass
    
    def forward_to_peer(self, message):
        try:
            self.peer_socket.sendall(message.encode())
        except:
            pass

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python server.py <port> <peer_port>")
        print("Example: python server.py 9000 9001")
        sys.exit(1)
    
    port = int(sys.argv[1])
    peer_port = int(sys.argv[2])
    
    server = ChatServer(port, peer_port)
    server.start()
