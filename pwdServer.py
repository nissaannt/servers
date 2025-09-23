#!/usr/bin/env python3
# pwd_server.py
"""
Password validation server.
Run:
    python3 pwd_server.py
"""

import socket
import threading
import re

HOST = '0.0.0.0'
PORT = 6000

# Precompiled regexes
ALLOWED_RE = re.compile(r'^[A-Za-z0-9_@\$]+$')
UPPER_RE = re.compile(r'[A-Z]')
DIGIT_RE = re.compile(r'[0-9]')
SPECIAL_RE = re.compile(r'[_@\$]')

def validate_password(pwd):
    """
    Returns (is_valid:bool, reasons:list[str])
    """
    reasons = []

    if not (8 <= len(pwd) <= 20):
        reasons.append("Length must be between 8 and 20 characters.")

    if not ALLOWED_RE.match(pwd):
        reasons.append("Contains invalid characters. Allowed: A-Z a-z 0-9 and _ @ $ only.")

    if not UPPER_RE.search(pwd):
        reasons.append("Must contain at least one uppercase letter [A-Z].")

    if not DIGIT_RE.search(pwd):
        reasons.append("Must contain at least one digit [0-9].")

    if not SPECIAL_RE.search(pwd):
        reasons.append("Must contain at least one special character from: _ @ $.")

    return (len(reasons) == 0, reasons)

def handle_client(conn, addr):
    print(f"[+] Client connected: {addr}")
    try:
        with conn:
            f = conn.makefile('r')   # read lines conveniently
            for line in f:
                pwd = line.rstrip('\n')
                if pwd == '':
                    # ignore empty lines
                    continue
                # Allow clients to request close
                if pwd.lower() in ('quit', 'exit'):
                    conn.sendall(b"Goodbye.\n")
                    break

                valid, reasons = validate_password(pwd)
                if valid:
                    resp = "Valid password.\n"
                else:
                    resp = "Invalid password: " + "; ".join(reasons) + "\n"

                conn.sendall(resp.encode('utf-8'))
    except Exception as e:
        print(f"[!] Error with client {addr}: {e}")
    finally:
        print(f"[-] Client disconnected: {addr}")

def start_server():
    print(f"Starting Password Validation Server on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

if __name__ == '__main__':
    start_server()
