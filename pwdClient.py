#!/usr/bin/env python3
# pwd_client.py
"""
Interactive password validation client.
Run:
    python3 pwd_client.py
You can pass host and port as optional args:
    python3 pwd_client.py localhost 6000
"""

import socket
import sys
import getpass

def run_client(host='localhost', port=6000):
    try:
        with socket.create_connection((host, port)) as sock:
            print(f"Connected to password server at {host}:{port}")
            f = sock.makefile('r')  # for reading server responses
            while True:
                try:
                    pwd = getpass.getpass("Enter password (or type 'quit' to exit): ")
                except (KeyboardInterrupt, EOFError):
                    print("\nExiting client.")
                    break

                if not pwd:
                    print("Empty input — try again.")
                    continue

                # send password (one line)
                sock.sendall((pwd + '\n').encode('utf-8'))

                # read server response line
                resp = f.readline()
                if not resp:
                    print("Server closed connection.")
                    break
                print("Server:", resp.strip())

                if pwd.lower() in ('quit', 'exit'):
                    break
    except ConnectionRefusedError:
        print("Could not connect to server. Ensure server is running and reachable.")
    except Exception as e:
        print("Client error:", e)

if __name__ == '__main__':
    host = 'localhost'
    port = 6000
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])
    run_client(host, port)
