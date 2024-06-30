from scapy.all import *
import ipaddress


def packet_handler(pkt, ip_range):
    if IP in pkt:
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst

        # Check if source or destination IP is in the specified range
        if ip_in_range(src_ip, ip_range) or ip_in_range(dst_ip, ip_range):
            print(f'IP Packet: {src_ip} -> {dst_ip}')
            # Optionally, you can print more details about the packet
            print(pkt.summary())  # Print summary of the packet
            print(pkt.show())  # Show detailed information about the packet
            print('-' * 50)


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


if __name__ == '__main__':
    # Input from user
    interface = input("Enter network interface (e.g., 'en0'): ")
    start_ip = input("Enter start IP address of range: ")
    end_ip = input("Enter end IP address of range: ")
    ip_range = (start_ip, end_ip)
    count = int(input("Enter number of packets to capture: "))

    # Start packet capture
    start_sniffing(interface, ip_range, count)
