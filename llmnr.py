# Test script for detecting LLMNR spoofing

# Import packages
from scapy.all import *
import threading
import random
import string
import logger

# Global variables
try:
    SLEEP_TIME = int(os.environ['LLMNR_SLEEP']) # number of seconds to sleep between requests
except:
    logger.error("Invalid llmnr sleep time provided.  Must be int")
    exit(1)
DESTINATION_IP = '224.0.0.252' # multicast address for LLMNR

# Function to generate random hostnames
# Used microsofts DNS naming conventions https://support.microsoft.com/en-us/help/909264/naming-conventions-in-active-directory-for-computers-domains-sites-and
def generate_name():
    string_length = random.randint(2, 63)
    letters_and_digits = string.ascii_letters + string.digits + '.'
    return ''.join(random.choice(letters_and_digits) for i in range(string_length))

# Function to send requests
def sender():
    while 1:
        source_port = random.randint(49152, 65535)
        id = random.randint(1, 65535)
        query_name = generate_name()
        pkt = IP(dst=DESTINATION_IP, ttl=1)/UDP(sport=source_port,dport=5355)/LLMNRQuery(id=id, qr=0, qdcount=1, ancount=0, nscount=0, arcount=0, qd=DNSQR(qname=query_name))

        send (pkt, verbose=0)
        time.sleep(SLEEP_TIME)

# Handler for incoming responses
def get_packet(pkt):
    if not pkt.getlayer(LLMNRResponse):
        return
    if (pkt.qr == 1) & (pkt.opcode == 0) & (pkt.c == 0) & (pkt.tc == 0) & (pkt.rcode == 0):
        # Get the machine name from the LLMNR response
        response_name = str(pkt.qd.qname, 'utf-8')
        logger.warning(f'A spoofed LMNR response for {response_name} was detected by from host {pkt.getlayer(IP).src} - {pkt.getlayer(Ether).src}')

#Function for starting sniffing
def listen():
    sniff(filter="udp and port 5355",store=0,prn=get_packet)

# Main function
def init():
    try:
        try:
            logger.info("Starting LLMNR UDP Response Server...")
            threading.Thread(target=listen).start()
            logger.info("Starting LLMNR Request Thread...")
            threading.Thread(target=sender).start()
        except:
            logger.error("Server could not be started, confirm you're running this as root.\n")
            exit(1)
    except:
        logger.error("Server could not be started, confirm you're running this as root.\n")
        exit(1)