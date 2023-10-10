import csv
from datetime import datetime
from scapy.all import *
import time
import numpy as np
import time

from IMUCollect import imu_collect

"""
Run monitor_mode.sh first to set up the network adapter to monitor mode and to
set the interface to the right channel.
To get RSSI values, we need the MAC Address of the connection 
of the device sending the packets.
"""

# Variables to be modified
dev_mac = "e4:5f:01:d4:9f:f9"  # Assigned transmitter MAC
iface_n = "wlan1"  # Interface for network adapter
duration = 30  # Number of seconds to sniff for
file_name = "IMU/rssi.csv"  # Name of CSV file where RSSI values are stored


def create_rssi_file():
    """Create and prepare a file for RSSI values"""
    header = ["timestamp", "mac_1", "mac_2", "rssi"]
    with open(file_name, "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def captured_packet_callback(pkt):
    """Save MAC addresses, time, and RSSI values to CSV file if MAC address of src matches"""
    cur_dict = {}
    try:
        cur_dict["mac_1"] = pkt.addr1
        cur_dict["mac_2"] = pkt.addr2
        cur_dict["rssi"] = pkt.dBm_AntSignal
    except AttributeError:
        return  # Packet formatting error

    timestamp=time.time()

    ################### Your code here ###################

    # Only write the RSSI values of packets that are coming from your assigned transmitter (hint: filter by pkt.addr2, the destination MAC field)
    # Use the 'writerow' method to write the RSSI value and the current timestamp to the CSV file

    ######################################################
    if pkt.haslayer(Dot11) and cur_dict["mac_2"] == dev_mac:
        with open(file_name, mode = "a", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([timestamp, cur_dict["mac_1"], cur_dict["mac_2"], cur_dict["rssi"]])


if __name__ == "__main__":
    create_rssi_file()

    t = AsyncSniffer(iface=iface_n, prn=captured_packet_callback, store=0)
    t.daemon = True
    t.start()
    
    start_date_time = datetime.now().strftime("%d/%m/%Y,%H:%M:%S.%f") #Get current date and time
    imu_collect(duration)

    t.stop()

    print("Start Time: ", start_date_time)
