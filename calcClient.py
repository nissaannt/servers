#!/usr/bin/env python3
# calc_client.py

import socket
import sys

def run_client(server_host='localhost', server_port=5000):
    name = None
    if len(sys.argv) >= 2:
        name = sys.argv[1]
    try:
        with socket.create_connection((server_host, server_port)) as sock:
            print(f"Connected to calculator server at {server_host}:{server_port}")
            print("Enter calculation in form: <operand1> <operator> <operand2>  (e.g. 12 + 5)")
            print("Type 'quit' or 'exit' to close client.")
            # file-like reader
            f = sock.makefile('r')
            while True:
                try:
                    line = input("Enter: ").strip()
                except EOFError:
                    break
                if not line:
                    continue
                sock.sendall((line + '\n').encode('utf-8'))
                # read one response line
                resp = f.readline()
                if not resp:
                    print("Server closed connection.")
                    break
                print(resp.strip())
                if line.lower() in ('quit','exit'):
                    print("Exiting client.")
                    break
    except ConnectionRefusedError:
        print("Could not connect to server. Ensure the server is running.")
    except Exception as e:
        print("Client error:", e)

if __name__ == '__main__':
    # optional CLI args: host port
    host = 'localhost'
    port = 5000
    if len(sys.argv) >= 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
    elif len(sys.argv) == 2:
        # if one arg given treat it as name only, keep default host/port
        pass
    run_client(host, port)
