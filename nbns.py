# Test script for detecting netbios name service spoofing
# All the hard work was done by someone else here https://github.com/NetSPI/SpoofSpotter

# Import packages
from scapy.all import *
import threading
import random
import string
import ipaddress
import logger
import alert_handler

# Function to generate random hostnames between with a length of 1-15 per netbios spec
# https://en.wikipedia.org/wiki/NetBIOS
def generate_name():
    string_length = random.randint(1, 15)
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(string_length))

# Function to send requests
def sender():
    try:
        SLEEP_TIME = int(os.environ['NBNS_SLEEP']) # number of seconds to sleep between requests
    except:
        logger.error("Invalid netbios sleep time provided.  Must be int")
        exit(1)

    BROADCAST_IP = os.environ['BROADCAST_IP'] # get broadcast address from docker environmental variable

    # Verify the provided broadcast address.
    if BROADCAST_IP == '':
        logger.error("You must supply a value for BROADCAST_IP in the container startup command.")
        logger.error("Example -e BROADCAST_IP=192.168.1.255")
        exit(1)

    try:
        ipaddress.ip_address(BROADCAST_IP)
    except:
        logger.error(f'{BROADCAST_IP} is not a valid ip address')
        exit(1)

    # Send packets in loop
    while 1:
        query_name = generate_name()
        pkt = IP(dst=BROADCAST_IP)/UDP(sport=137, dport='netbios_ns')/NBNSQueryRequest(SUFFIX="file server service",QUESTION_NAME=query_name, QUESTION_TYPE='NB')
        send (pkt, verbose=0)
        time.sleep(SLEEP_TIME)

# Handler for incoming NBNS responses
def get_packet(pkt):
    if not pkt.getlayer(NBNSQueryRequest):
        return
    if pkt.FLAGS == 0x8500:
        # Get the machine name from the NBNS response
        response_name = str(pkt.getlayer(NBNSQueryRequest).QUESTION_NAME).split("'")[1].rstrip()
        logger.warning(f'A spoofed NBNS response for {response_name} was detected by from host {pkt.getlayer(IP).src} - {pkt.getlayer(Ether).src}')

        # Send message to alert handler
        alert_handler.new_alert("nbns", pkt.getlayer(IP).src, pkt.getlayer(Ether).src, f'NBNS response for {response_name}')

#Function for starting sniffing
def listen():
    sniff(filter="udp and port 137",store=0,prn=get_packet)

# Main function
def init():
    try:
        try:
            logger.info("Starting NBNS UDP Response Server...")
            threading.Thread(target=listen).start()
            logger.info("Starting NBNS Request Thread...")
            threading.Thread(target=sender).start()
        except:
            logger.error("Server could not be started, confirm you're running this as root.\n")
            exit(1)
    except:
        logger.error("Server could not be started, confirm you're running this as root.\n")
        exit(1)