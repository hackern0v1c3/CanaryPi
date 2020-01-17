# Test script for detecting mDNS spoofing

# Import modules
from scapy.all import *
import threading
import random
import string
import logger
import alert_handler

# Function to generate random hostnames
# Used microsofts DNS naming conventions https://support.microsoft.com/en-us/help/909264/naming-conventions-in-active-directory-for-computers-domains-sites-and
def generate_name():
    string_length = random.randint(2, 63)
    letters_and_digits = string.ascii_letters + string.digits + '.'
    return ''.join(random.choice(letters_and_digits) for i in range(string_length))

# Function to send requests
def sender():
    try:
        SLEEP_TIME = int(os.environ['MDNS_SLEEP']) # number of seconds to sleep between requests
    except:
        logger.error("Invalid mdns sleep time provided.  Must be int")
        exit(1)

    DESTINATION_IP = '224.0.0.251' # multicast address for mDNS

    while 1:
        source_port = random.randint(49152, 65535)
        id = random.randint(1, 65535)
        query_name = generate_name()
        #pkt = IP(dst=DESTINATION_IP, ttl=1)/UDP(sport=source_port,dport=5355)/LLMNRQuery(id=id, qr=0, qdcount=1, ancount=0, nscount=0, arcount=0, qd=DNSQR(qname=query_name))
        pkt = IP(dst=DESTINATION_IP, ttl=1)/UDP(sport=source_port,dport=5353)/DNS(id=id, qr=0, qdcount=1, ancount=0, nscount=0, rd=1, arcount=0, qd=DNSQR(qname=query_name))

        logger.debug(f'Sending MDNS spoofed packet')
        send (pkt, verbose=0)
        time.sleep(SLEEP_TIME)

# Handler for incoming responses
def get_packet(pkt):
    # rfc https://tools.ietf.org/html/rfc6762#section-6
    # response source port must be 5353
    # destination port must be 5353
    # response ip must be 224.0.0.251 or ipv6 FF02::FB

    if not pkt.getlayer(DNS):
        return
    
    src_ip = pkt.getlayer(IP).src
    dst_ip = pkt.getlayer(IP).dst
    dst_port = pkt.getlayer(IP).dport
    src_port = pkt.getlayer(IP).sport

    if (dst_ip == '224.0.0.251') & (dst_port == 5353) & (src_port == 5353) & (pkt.qr == 1) & (pkt.opcode == 0) & (pkt.rcode == 0):
        # Get the machine name from the mdns response
        response_name = str(DNSRR(pkt.an[0]).rrname, 'utf-8')

        logger.warning(f'A spoofed MDNS response for {response_name} was detected by from host {pkt.getlayer(IP).src} - {pkt.getlayer(Ether).src}')

        # Send message to alert handler
        alert_handler.new_alert("mdns", pkt.getlayer(IP).src, pkt.getlayer(Ether).src, f'MDNS response for {response_name}')

#Function for starting sniffing
def listen():
    sniff(filter="udp and dst host 224.0.0.251 and port 5353",store=0,prn=get_packet)

# Main function
def init():
    try:
        logger.info("Starting MDNS UDP Response Server...")
        threading.Thread(target=listen).start()
        logger.info("Starting MDNS Request Thread...")
        threading.Thread(target=sender).start()
    except:
        logger.error("Server could not be started, confirm you're running this as root.\n")
        exit(1)