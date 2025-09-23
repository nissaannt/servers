#!/usr/bin/env python3
"""
weather_client.py
Interactive client for the weather server.

Usage:
    python3 weather_client.py [host] [port]

Defaults: host=localhost port=5500
"""
import socket
import sys
import json

HOST = 'localhost'
PORT = 5500
if len(sys.argv) >= 2:
    HOST = sys.argv[1]
if len(sys.argv) >= 3:
    PORT = int(sys.argv[2])

def format_report(resp):
    """Pretty print the JSON response from server."""
    status = resp.get('status')
    if status == 'ok':
        lines = []
        lines.append(f"Weather report for {resp.get('city')}:")
        lines.append(f"  Condition     : {resp.get('condition')}")
        lines.append(f"  Temperature   : {resp.get('temperature_c')} °C")
        lines.append(f"  Feels like    : {resp.get('feels_like_c')} °C")
        lines.append(f"  Humidity      : {resp.get('humidity_pct')} %")
        lines.append(f"  Wind speed    : {resp.get('wind_kph')} kph")
        from datetime import datetime
        ts = resp.get('timestamp')
        if ts:
            lines.append("  Time (UTC)    : " + datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
        return '\n'.join(lines)
    elif status == 'bye':
        return resp.get('message', 'Goodbye from server.')
    else:
        return "Error from server: " + resp.get('message', 'Unknown error')

def run_client(host, port):
    try:
        with socket.create_connection((host, port)) as sock:
            print(f"Connected to weather server at {host}:{port}")
            reader = sock.makefile('r')
            while True:
                try:
                    city = input("Enter city (or 'quit' to exit): ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\nExiting client.")
                    break
                if not city:
                    continue
                sock.sendall((city + '\n').encode('utf-8'))
                # read one JSON response line
                line = reader.readline()
                if not line:
                    print("Server closed connection.")
                    break
                try:
                    resp = json.loads(line)
                except Exception:
                    print("Received malformed response:", line)
                    continue
                print(format_report(resp))
                if city.lower() in ('quit', 'exit'):
                    break
    except ConnectionRefusedError:
        print("Could not connect to server. Make sure the server is running.")
    except Exception as e:
        print("Client error:", e)

if __name__ == '__main__':
    run_client(HOST, PORT)
