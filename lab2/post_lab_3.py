import ipaddress
from scapy.all import *
import time
from datetime import datetime


def filter_packet(packet, ip_addr, protocol, pkg_length, start_time = None, end_time = None):
    if IP in packet and protocol in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        packet_length = len(packet[protocol].payload)
        packet_time = packet.time

        if ((src_ip == ip_addr or dst_ip == ip_addr) and
            packet_length > pkg_length
        ):
            return True
    return False


def motion_detected(pcap_file: str) -> list:
    inter_packet_times = []
    payload_length = []
    repeated_packets = {}
    packets = rdpcap(pcap_file)
    
    router_ip = "172.16.136.219"
    mask = "255.255.128.0"

    for i in range(1, len(packets)):
        packet = packets[i]
        # print(packet[IP].src, packet[IP].dst, len(packet[UDP].payload))
        if filter_packet(packet, ip_addr=router_ip, protocol=UDP, pkg_length=500):
            # If it is a valid packet from/to ip_addr, with protocol and minimum pkg_length
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            payload_len = len(packet[UDP].payload)
            # Check if src is in LAN and src not the router
            if ipaddress.IPv4Network(f"{src_ip}/{mask}", strict=False) == ipaddress.IPv4Network(f"{router_ip}/{mask}", strict=False) and src_ip != router_ip:
                packet_key = (src_ip, dst_ip, payload_len)
                repeated_packets.setdefault(packet_key, 0)
                repeated_packets[packet_key] += 1
            inter_packet_times.append(packets[i].time - packets[i-1].time)
            payload_length.append(payload_len)
    
    single_packets_key = []
    for packet_key in repeated_packets:
        if repeated_packets[packet_key] < 5:
            single_packets_key.append(packet_key)
    for packet_key in single_packets_key:
        del repeated_packets[packet_key]

    return repeated_packets


if __name__ == "__main__":
    pcap_file = "packet_capture.pcap"
    repeated_packets = motion_detected(pcap_file)
    print(repeated_packets)

