#!/usr/bin/env python3
"""
weather_server.py
A simple multithreaded TCP server that simulates weather data for cities.

Usage:
    python3 weather_server.py [port]

Default port: 5500
"""
import socket
import threading
import json
import time
import random
import sys

HOST = '0.0.0.0'
PORT = 5500
if len(sys.argv) >= 2:
    PORT = int(sys.argv[1])

# Hardcoded base weather data for some cities (values are averages)
BASE_WEATHER = {
    'new york':   {'temp_c': 15.0, 'humidity': 60, 'conditions': ['Cloudy', 'Sunny', 'Rain']},
    'london':     {'temp_c': 12.0, 'humidity': 70, 'conditions': ['Rain', 'Cloudy', 'Fog']},
    'mumbai':     {'temp_c': 29.0, 'humidity': 75, 'conditions': ['Sunny', 'Humid', 'Showers']},
    'tokyo':      {'temp_c': 18.0, 'humidity': 65, 'conditions': ['Sunny', 'Cloudy', 'Rain']},
    'sydney':     {'temp_c': 20.0, 'humidity': 55, 'conditions': ['Sunny', 'Windy', 'Cloudy']},
    'delhi':      {'temp_c': 28.0, 'humidity': 50, 'conditions': ['Hot', 'Hazy', 'Sunny']},
}

def simulate_weather(city_lower):
    """
    Return a dict with simulated weather data for the city.
    If city is known in BASE_WEATHER, use base values + small randomness.
    """
    base = BASE_WEATHER.get(city_lower)
    if not base:
        return None

    # add small random variation to make each request slightly different
    temp = round(base['temp_c'] + random.uniform(-3.0, 3.0), 1)
    humidity = max(10, min(100, int(base['humidity'] + random.uniform(-8, 8))))
    condition = random.choice(base['conditions'])

    # Compute a simple "feels like" (very rough)
    feels_like = temp
    if temp >= 30:
        feels_like = round(temp + (humidity - 50) * 0.05, 1)
    elif temp < 10:
        feels_like = round(temp - (50 - humidity) * 0.02, 1)

    # wind simulated
    wind_kph = round(abs(random.gauss(10, 4)), 1)

    return {
        'city': city_lower.title(),
        'temperature_c': temp,
        'feels_like_c': feels_like,
        'humidity_pct': humidity,
        'condition': condition,
        'wind_kph': wind_kph,
        'timestamp': int(time.time()),
        'status': 'ok'
    }

def handle_client(conn, addr):
    print(f"[+] Client connected: {addr}")
    try:
        with conn:
            f = conn.makefile('r')  # read lines
            while True:
                line = f.readline()
                if not line:
                    break  # client closed
                city = line.strip()
                if not city:
                    # ignore empty lines
                    continue
                if city.lower() in ('quit', 'exit'):
                    # allow client to close politely
                    conn.sendall((json.dumps({'status':'bye', 'message':'Goodbye'}) + '\n').encode('utf-8'))
                    break

                # Simulate lookup
                city_key = city.lower()
                data = simulate_weather(city_key)
                if data is None:
                    # Not found — respond with error plus a small simulated fallback (optional)
                    resp = {
                        'status': 'error',
                        'message': f"No hardcoded data for city '{city}'. Try one of: {', '.join(k.title() for k in BASE_WEATHER.keys())}"
                    }
                else:
                    resp = data

                # send response as single-line JSON
                conn.sendall((json.dumps(resp) + '\n').encode('utf-8'))
    except Exception as e:
        print(f"[!] Error with client {addr}: {e}")
    finally:
        print(f"[-] Client disconnected: {addr}")

def start_server(host, port):
    print(f"Starting Weather Server on {host}:{port}")
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
