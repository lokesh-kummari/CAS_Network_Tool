from flask import Flask, render_template, request
from scapy.all import *
import ipaddress

app = Flask(__name__)

# List to store captured packets
captured_packets = []


def packet_handler(pkt, ip_range):
    if IP in pkt:
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst

        # Check if source or destination IP is in the specified range
        if ip_in_range(src_ip, ip_range) or ip_in_range(dst_ip, ip_range):
            # Prepare packet information
            packet_info = {
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'summary': pkt.summary(),
                'details': str(pkt.show(dump=True))  # Convert show() output to string
            }
            captured_packets.append(packet_info)
            print(f'Captured Packet: {src_ip} -> {dst_ip}')
            print(pkt.summary())
            print(pkt.show())
            print('-' * 50)

            # Limit captured packets to 50 for display
            if len(captured_packets) > 50:
                captured_packets.pop(0)


def ip_in_range(ip_addr, ip_range):
    # ip_range should be a tuple (start_ip, end_ip)
    start_ip = ipaddress.IPv4Address(ip_range[0])
    end_ip = ipaddress.IPv4Address(ip_range[1])
    ip_to_check = ipaddress.IPv4Address(ip_addr)

    return start_ip <= ip_to_check <= end_ip


def start_sniffing(interface, ip_range, count):
    print(f"Sniffing {count} packets on interface {interface}...")
    sniff(iface=interface, prn=lambda pkt: packet_handler(pkt, ip_range), count=count)
    print("Sniffing complete.")


@app.route('/')
def index():
    return render_template('index1.html', packets=captured_packets)


@app.route('/start_capture', methods=['POST'])
def start_capture():
    data = request.form
    interface = data['interface']
    start_ip = data['start_ip']
    end_ip = data['end_ip']
    count = int(data['count'])

    # Start packet capture in a separate thread
    import threading
    capture_thread = threading.Thread(target=start_sniffing, args=(interface, (start_ip, end_ip), count))
    capture_thread.start()

    return 'Packet capture started successfully.'


if __name__ == '__main__':
    app.run(debug=True, port=8000)  # Specify the port as 8000
