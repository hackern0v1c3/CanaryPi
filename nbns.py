# Test script for detecting netbios name service spoofing
# All the hard work was done by someone else here https://github.com/NetSPI/SpoofSpotter

# Import packages
from scapy.all import *
import threading

# Global variables
QUERY_NAME = 'badname' # name to look for on network.  Should be randomized
SENT = 'false'
BADIPs = []
DESTINATION_IP = '224.0.0.252' # multicast address for netbios
SLEEP_TIME = 10 # number of seconds to sleep between requests

# Scapy broadcast packet creation
pkt = IP(dst=DESTINATION_IP)/UDP(sport=137, dport='netbios_ns')/NBNSQueryRequest(SUFFIX="file server service",QUESTION_NAME=QUERY_NAME, QUESTION_TYPE='NB')

# Function to send requests
def sender():
    while 1:
        send (pkt, verbose=0)
        time.sleep(SLEEP_TIME)

#Handler for incoming NBNS responses
def get_packet(pkt):
    if not pkt.getlayer(NBNSQueryRequest):
        return
    if pkt.FLAGS == 0x8500:
        print(f'A spoofed NBNS response for {QUERY_NAME} was detected by from host {pkt.getlayer(IP).src} - {pkt.getlayer(Ether).src}')
        logged = 0
        for i in BADIPs:
            if i == pkt.getlayer(IP).src:
                logged = 1
        if logged == 0:
            BADIPs.append(str(pkt.getlayer(IP).src))
            global SENT
            SENT = 'false'

# Main function
def main():
    try:
        print ("Starting NBNS Request Thread...")
        threading.Thread(target=sender).start()
        try:
            print ("Starting UDP Response Server...")
            sniff(filter="udp and port 137",store=0,prn=get_packet)
        except KeyboardInterrupt:
            print ("\nStopping Server and Exiting...\n")
        except:
            print ("Server could not be started, confirm you're running this as root.\n")
    except KeyboardInterrupt:
        exit()
    except:
        print ("Server could not be started, confirm you're running this as root.\n")

# Launch main
main()