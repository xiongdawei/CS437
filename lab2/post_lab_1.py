import matplotlib.pyplot as plt
from scapy.all import *


def motion_detected(pcap_file: str) -> list:
    motions = []
    packets = rdpcap(pcap_file)
    
    start_time = None

    for packet in packets:
        if start_time is None:
            start_time = packet.time
        if UDP in packet and packet[UDP].payload:
            payload = str(packet[UDP].payload)
            if "detected" in payload:
                motions.append(packet.time - start_time)

    return motions

def plot_motion_detected(motions: list):
    print(motions)
    plt.figure()
    plt.scatter(motions, [1] * len(motions), marker="o", color="blue")
    plt.xlabel("Timestamp [seconds]")
    plt.ylabel("Is motion detected?")
    plt.xlim(xmin=0.0)
    plt.ylim((0.0, 1.2))
    plt.title("Motion Detection Timeline")
    plt.show()


if __name__ == "__main__":
    pcap_file = "packet_capture.pcap"
    motions = motion_detected(pcap_file)
    plot_motion_detected(motions)

