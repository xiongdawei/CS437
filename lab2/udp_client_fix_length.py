import socket

message = "Motion detected!!!!!" * 50  # a large packet
ip_addr = "172.16.136.219"
port_num = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
sock.sendto(bytes(message, "utf-8"), (ip_addr, port_num))
