#!/usr/bin/env python3
# calc_server.py

import socket
import threading

HOST = '0.0.0.0'
PORT = 5000

def calculate(op1_str, operator, op2_str):
    try:
        a = float(op1_str)
        b = float(op2_str)
    except ValueError:
        return "Error: operands must be numbers."

    try:
        if operator == '+':
            res = a + b
        elif operator == '-':
            res = a - b
        elif operator == '*' or operator.lower() == 'x':
            res = a * b
        elif operator == '/':
            if b == 0:
                return "Error: division by zero."
            res = a / b
        elif operator == '%':
            res = a % b
        elif operator == '^' or operator == '**':
            res = a ** b
        else:
            return f"Error: unsupported operator '{operator}'. Supported: + - * / % ^"
    except Exception as e:
        return f"Error: {e}"

    # Return as float or integer nicely
    if res.is_integer():
        return f"Result: {int(res)}"
    else:
        return f"Result: {res}"

def handle_client(conn, addr):
    print(f"[+] Connected by {addr}")
    try:
        with conn:
            # make a file-like wrapper for easy readline()
            f = conn.makefile('r')
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # protocol: "operand1 operator operand2"
                parts = line.split()
                if len(parts) != 3:
                    response = "Error: send in format: <operand1> <operator> <operand2>  (e.g. 12 + 5)"
                else:
                    op1, operator, op2 = parts
                    response = calculate(op1, operator, op2)
                conn.sendall((response + '\n').encode('utf-8'))
                # optionally close if client asked to exit
                if line.lower() in ('exit', 'quit'):
                    break
    except Exception as e:
        print(f"[!] Client {addr} error: {e}")
    finally:
        print(f"[-] Disconnected {addr}")

def start_server():
    print(f"Starting Calculator Server on {HOST}:{PORT}")
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
