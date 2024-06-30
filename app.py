from flask import Flask, render_template, request, jsonify
import socket
import concurrent.futures  # Import for ThreadPoolExecutor
from scapy.all import srp, Ether, ARP
import time  # Import time module for adding delays

app = Flask(__name__)

def scan_network(ip_range):
    print("Scanning network for devices...\n")
    devices = []
    try:
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range), timeout=10, verbose=False, inter=0.1)  # Add inter parameter for delay between packets
        devices = [(pkt[1].psrc, pkt[1].src) for pkt in ans]
        devices_info = []

        if devices:
            print("Found active devices:")
            for i, (ip, mac) in enumerate(devices, start=1):
                print(f"Device {i}:")
                print(f"  IP Address: {ip}")
                print(f"  MAC Address: {mac}")
                print("  Status: Online")
                open_ports = scan_ports(ip)
                print(f"  Open Ports: {open_ports}")
                print()
                devices_info.append({
                    "ip": ip,
                    "mac": mac,
                    "ports": open_ports
                })
        else:
            print("No active devices found in the specified IP range.")
    except Exception as e:
        print(f"An error occurred during scanning: {str(e)}")

    return devices_info


def scan_ports(ip_address):
    open_ports = []
    print(f"Scanning ports for {ip_address}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for port in range(1, 1025):
            futures.append(executor.submit(scan_port, ip_address, port))
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result != -1:
                open_ports.append(result)
    return open_ports

def scan_port(ip_address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)  # Adjust timeout as necessary
        result = s.connect_ex((ip_address, port))
        if result == 0:
            return port
    return -1

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    ip_range = data.get('ip_range')
    devices_info = scan_network(ip_range)
    return jsonify(devices=devices_info)


if __name__ == "__main__":
    app.run(debug=True)
