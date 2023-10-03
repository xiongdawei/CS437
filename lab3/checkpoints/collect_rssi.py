import csv
from datetime import datetime
from scapy.all import *
import time

"""
Run monitor_mode.sh first to set up the network adapter to monitor mode and to
set the interface to the right channel.
To get RSSI values, we need the MAC Address of the connection 
of the device sending the packets.
"""

# Variables to be modified
dev_mac = ""  # Assigned transmitter MAC
iface_n = "wlan1"  # Interface for network adapter
duration = 30  # Number of seconds to sniff for
file_name = "rssi.csv"  # Name of CSV file where RSSI values are stored


def create_rssi_file():
    """Create and prepare a file for RSSI values"""
    header = ["date", "time", "dest", "src", "rssi"]
    with open(file_name, "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def captured_packet_callback(pkt):
    """Save MAC addresses, time, and RSSI values to CSV file if MAC address of src matches"""
    missed_count = 0  # Number of missed packets while attempting to write to file

    cur_dict = {}
    try:
        cur_dict["mac_1"] = pkt.addr1
        cur_dict["mac_2"] = pkt.addr2
        cur_dict["rssi"] = pkt.dBm_AntSignal
    except AttributeError:
        return  # Packet formatting error

    date_time = datetime.now().strftime("%d/%m/%Y,%H:%M:%S.%f").split(",") #Get current date and time
    date = date_time[0]
    time = date_time[1]

    ################### Your code here ###################

    # Only write the RSSI values of packets that are coming from your assigned transmitter (hint: filter by pkt.addr2, the destination MAC field)
    # Use the 'writerow' method to write the RSSI value and the current timestamp to the CSV file

    ######################################################
    target_mac = "e4:5f:01:d4:9d:2f"
    if pkt.haslayer(Dot11) and cur_dict["mac_2"]==target_mac:
        with open(file_name, mode = "a", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            #csv_write.writerow(['Time', 'RSSI'])
           # rssi = packet.dBm_AntSignal if hasattr(pkt, 'dBm_AntSignal') else None
            csv_writer.writerow([date, time, cur_dict['mac_1'], cur_dict['mac_2'],cur_dict['rssi']])


        


if __name__ == "__main__":
    create_rssi_file()

    t = AsyncSniffer(iface=iface_n, prn=captured_packet_callback, store=0)
    t.daemon = True
    t.start()
    
    start_date_time = datetime.now().strftime("%d/%m/%Y,%H:%M:%S.%f") #Get current date and time

    time.sleep(duration)
    t.stop()

    print("Start Time: ", start_date_time)
