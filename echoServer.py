#!/usr/bin/env python3
# echo_server.py
"""
Multi-client Echo Server.
Usage:
    python3 echo_server.py [port]
Default port: 5000
"""
import socket
import threading
import sys

HOST = '0.0.0.0'
PORT = 5000
if len(sys.argv) >= 2:
    PORT = int(sys.argv[1])

def handle_client(conn, addr):
    """Handle a single client: read lines and echo them back."""
    print(f"[+] Client connected: {addr}")
    try:
        # file-like object for convenient readline()
        with conn:
            f = conn.makefile('r', encoding='utf-8', newline='\n')
            for line in f:
                message = line.rstrip('\n')
                if message == '':
                    # ignore empty lines
                    continue
                print(f"[{addr}] Received: {message}")
                # echo back (add newline)
                try:
                    conn.sendall((message + '\n').encode('utf-8'))
                except BrokenPipeError:
                    break
                # optional close command
                if message.lower() in ('exit', 'quit', 'bye'):
                    break
    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        try:
            conn.close()
        except:
            pass
        print(f"[-] Client disconnected: {addr}")

def start_server(host, port):
    print(f"Starting Echo Server on {host}:{port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(8)
        try:
            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                t.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")

if __name__ == '__main__':
    start_server(HOST, PORT)
