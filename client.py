
import socket
import threading
import sys
import time

# Client configuration
client_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
username = f"User{client_id}"

def select_server():
    """Allow user to choose server or use round-robin"""
    print(f"\n=== Server Selection for {username} ===")
    print("1. Server 1 (port 8001)")
    print("2. Server 2 (port 8002)")
    print("3. Auto-select (round-robin)")
    
    while True:
        choice = input("Choose server (1/2/3): ").strip()
        
        if choice == '1':
            return 8001, "Server 1"
        elif choice == '2':
            return 8002, "Server 2"
        elif choice == '3':
            # Round-robin based on client_id
            if client_id % 2 == 1:
                return 8001, "Server 1 (auto-selected)"
            else:
                return 8002, "Server 2 (auto-selected)"
        else:
            print("Invalid choice! Please enter 1, 2, or 3")

SERVER_PORT, server_name = select_server()

def receive_messages(sock):
    """Receive and display messages from server"""
    while True:
        try:
            message = sock.recv(1024).decode()
            if not message:
                break
            print(f"\n{message}")
            print(f"{username}> ", end="", flush=True)
        except:
            print("\nDisconnected from server")
            break

def main():
    print(f"Client {client_id} ({username}) starting...")
    print(f"Connecting to {server_name} on port {SERVER_PORT}")
    
    # Connect to server
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', SERVER_PORT))
        print(f"Connected to {server_name}!")
        
        # Send join message
        join_msg = f"{username} joined the chat"
        client_socket.send(join_msg.encode())
        
        # Start message receiver thread
        receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receiver_thread.daemon = True
        receiver_thread.start()
        
        # Send messages
        print(f"\nYou can start chatting! (Type 'quit' to exit)")
        while True:
            message = input(f"{username}> ")
            
            if message.lower() == 'quit':
                client_socket.send(f"{username} left the chat".encode())
                break
                
            if message.strip():
                client_socket.send(f"{username}: {message}".encode())
        
        client_socket.close()
        print("Goodbye!")
        
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    main()
