import psutil
import threading
import subprocess
import scapy.all as sp

# Get a list of all TCP connections
tcp_connections = psutil.net_connections(kind='tcp')

# Get the list of ports with a connection
connected_ports = [conn.laddr.port for conn in tcp_connections if conn.status == psutil.CONN_ESTABLISHED]

# Print the list of connected ports
print(f"Connected ports: {connected_ports}")

list_request = []

interface = "lo"
create_dict = {}


def make_threads(list_connection):
    list_thread = []
    for i in list_connection:
        thread = threading.Thread(target=find, args=(i,))
        thread.start()
        list_thread.append(thread)
    return list_thread


def handle_packet(packet):
    # do something with the packet data
    print(packet)


def find(port: int):
    filter = "port " + str(port)

    all = sp.sniff(iface=interface, filter=filter, prn=handle_packet, timeout=30)

    print(all)
    if len(all) > 5:
        subprocess.run(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", f"{port}", "-j", "DROP"])


while True:
    list_thread = make_threads(connected_ports)
    for i in list_thread:
        i.join()
