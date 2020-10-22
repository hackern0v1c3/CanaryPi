# Test script for detecting port scanning

# Import modules
from scapy.all import *
import threading
import logger
import alert_handler
import netifaces

sniff_ports = []

# Verify that ports supplied by docker env are valid
def verify_tcp_ports():
    try:
        tcp_ports = os.environ['PORTSCAN_TCP_PORTS'].split(',')
        for port in tcp_ports:
            sniff_ports.append(int(port.strip()))
    except:
        logger.error("Invalid TCP ports provided.  Must be ints seperated by commas.  Example: '80, 443, 3389'")
        exit(1)

# Function to fetch all local mac address for building filter rules
def get_all_mac_addresses():
    mac_addresses = []

    # Fetch all local interfaces
    interfaces = netifaces.interfaces()

    # Try to fetch mac address for all local interfaces
    for interface in interfaces:
        try:
            addrs = netifaces.ifaddresses(interface)
            addr_data = addrs[netifaces.AF_LINK][0]
            mac = addr_data['addr']
            mac_addresses.append(mac)
        except:
            pass
    
    return mac_addresses

#Function to build filter fules for mac addresses
def build_mac_string():
    mac_addresses = get_all_mac_addresses()

    mac_string = mac_addresses.pop()

    for mac in mac_addresses:
        mac_string += f'or {mac}'
    
    return mac_string

# Function to build filter rules for multiple ports
def build_port_string(ports):
    port_string = f'dst port {sniff_ports.pop()}'
    for p in sniff_ports:
        port_string += f' or dst port {p}'
    return port_string

# Handler for incoming responses
def get_packet(pkt):
    src_mac = pkt.getlayer(Ether).src
    src_ip = pkt.getlayer(IP).src
    dst_ip = pkt.getlayer(IP).dst
    dst_port = pkt.getlayer(IP).dport

    logger.warning(f'Port scan detected: Mac address {src_mac} with IP address of {src_ip} tried connecting to {dst_ip}:{dst_port} ')
    # Send message to alert handler
    alert_handler.new_alert(f'portscan {dst_port}', src_ip, src_mac, f'Portscan connection request sent to {dst_ip}:{dst_port}')

#Function for starting sniffing
def listen():
    # Build sniffing filter.  Looks for TCP packets with destination to local mac address and specific destination ports
    tcp_filter = f'tcp and ether dst ({build_mac_string()}) and ({build_port_string(sniff_ports)})'

    sniff(filter=tcp_filter,store=0,prn=get_packet)

# Main function
def init():
    verify_tcp_ports()
    try:
        logger.info("Starting Port Scan Detection Server...")
        threading.Thread(target=listen).start()
    except:
        logger.error("Port scan detection server could not be started, confirm you're running this as root.\n")
        exit(1)
