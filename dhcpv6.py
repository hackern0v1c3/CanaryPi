# Test script for detecting rogue dhcpv6 servers

# Import modules
from scapy.all import *
from netaddr import *
import threading
import random
import string
import logger
import alert_handler
import ipaddress
import os

import codecs
decode_hex = codecs.getdecoder("hex_codec")

server_whitelist = []

#Function to generate the pieces for a random mac address
def generate_mac_pieces():
    random.seed()
    mac11 = str(hex(random.randint(0,255))[2:])
    mac12 = str(hex(random.randint(0,255))[2:])
    mac21 = str(hex(random.randint(0,255))[2:])
    mac22 = str(hex(random.randint(0,255))[2:])
    mac31 = str(hex(random.randint(0,255))[2:])
    mac32 = str(hex(random.randint(0,255))[2:])

    return [mac11, mac12, mac21, mac22, mac31, mac12]

def sender():
    try:
        SLEEP_TIME = int(os.environ['DHCPV6_SLEEP']) # number of seconds to sleep between requests
    except:
        logger.error("Invalid dhcpv6 sleep time provided.  Must be int")
        exit(1)

    # Generate a spoofed mac address rather than trying to fetch the actual one
    mac_pieces = generate_mac_pieces()
    mac_address = (':').join(mac_pieces)

    # Generate interface ID in EUI-64 format using the spoofed mac address
    eui64 = mac_pieces[0] + mac_pieces[1] + ":" + mac_pieces[2] + "ff" + ":" + "fe" + mac_pieces[3] + ":" + mac_pieces[4] + mac_pieces[5]

    # Generates Link-local  IPv6 addres in EUI-64 format
    ip6_ll_eui64 = "fe80" + "::" + eui64

    # Building and initilizing DHCPv6 SOLICIT packet layers with common parameters
    l2 = Ether()
    l2.dst = "33:33:00:01:00:02"

    l3 = IPv6()
    l3.src = ip6_ll_eui64
    l3.dst = "ff02::1:2"

    l4 = UDP()
    l4.sport = 546
    l4.dport = 547

    sol = DHCP6_Solicit()
    random.seed()
    sol.trid = random.randint(0,16777215)

    rc = DHCP6OptRapidCommit()
    rc.optlen = 0

    opreq = DHCP6OptOptReq()
    opreq.optlen = 4

    et= DHCP6OptElapsedTime()

    cid = DHCP6OptClientId()
    cid.optlen = 10
    cid.duid = (decode_hex("00030001"+str(EUI(mac_address)).replace("-",""))[0])

    iana = DHCP6OptIA_NA()
    iana.optlen = 12
    iana.T1 = 0
    iana.T2 = 0

    # Assembing the packet
    pkt = l2/l3/l4/sol/iana/rc/et/cid/opreq

    while 1:
        time.sleep(SLEEP_TIME)

        logger.debug(f'Sending DHCPv6 solicit packet')
        sendp (pkt,verbose=0)

# Handler for incoming DHCPV6 responses
def get_packet(pkt):
    if not pkt.getlayer(DHCP6_Advertise):
        return
    
    src_ip = pkt.getlayer(IPv6).src
    if src_ip in server_whitelist:
        return

    src_mac = pkt.getlayer(Ether).src

    logger.warning(f'A DHCPv6 Server has been detected on your network at {src_ip} - {src_mac}')
    alert_handler.new_alert("dhcpv6", src_ip, src_mac, f'DHCPv6 server detected {src_ip}')

#Function for starting sniffing
def listen():
    sniff(filter="udp and port 546",store=0,prn=get_packet)

# Main function
def init():
    if os.environ['DHCPV6_WHITELIST'] != "":
        try:
            whitelist = os.environ['DHCPV6_WHITELIST'].split(",")

            for server in whitelist:
                ipaddress.IPv6Address(server.strip())
                server_whitelist.append(server.strip())
        except:
            logger.error("Could not parse DHCP whitelist.  It must be a comma seperated list of ipv6 addresses")
            exit(1)
    try:
        logger.info("Starting DHCPv6 Response Server...")
        threading.Thread(target=listen).start()
        logger.info("Starting DHCPv6 Request Thread...")
        threading.Thread(target=sender).start()
    except:
        logger.error("Server could not be started, confirm you're running this as root.\n")
        exit(1)