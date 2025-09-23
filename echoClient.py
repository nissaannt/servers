#!/usr/bin/env python3
# echo_client.py
"""
Interactive Echo Client.
Usage:
    python3 echo_client.py [host] [port]
Defaults: host=localhost port=5000
"""
import socket
import sys

HOST = 'localhost'
PORT = 5000
if len(sys.argv) >= 2:
    HOST = sys.argv[1]
if len(sys.argv) >= 3:
    PORT = int(sys.argv[2])

def run_client(host, port):
    try:
        with socket.create_connection((host, port)) as sock:
            print(f"Connected to echo server at {host}:{port}")
            reader = sock.makefile('r', encoding='utf-8', newline='\n')
            while True:
                try:
                    text = input("You: ")
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting client.")
                    break
                if not text:
                    continue
                # send
                try:
                    sock.sendall((text + '\n').encode('utf-8'))
                except BrokenPipeError:
                    print("Connection to server lost.")
                    break
                # wait for echo
                resp = reader.readline()
                if not resp:
                    print("Server closed connection.")
                    break
                print("Echo:", resp.rstrip('\n'))
                if text.lower() in ('exit', 'quit', 'bye'):
                    break
    except ConnectionRefusedError:
        print(f"Could not connect to {host}:{port} — is the server running?")
    except Exception as e:
        print("Client error:", e)

if __name__ == '__main__':
    run_client(HOST, PORT)
