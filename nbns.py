# Test script for detecting netbios name service spoofing
# All the hard work was done by someone else here https://github.com/NetSPI/SpoofSpotter

# Import packages
from scapy.all import *
import threading
import random
import string

# Global variables
DESTINATION_IP = '224.0.0.252' # multicast address for netbios
SLEEP_TIME = 10 # number of seconds to sleep between requests

# Function to generate random hostnames between with a length of 1-15 per netbios spec
# https://en.wikipedia.org/wiki/NetBIOS
def generateName():
    stringLength = random.randint(1, 15)
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

# Function to send requests
def sender():
    while 1:
        query_name = generateName()
        pkt = IP(dst=DESTINATION_IP)/UDP(sport=137, dport='netbios_ns')/NBNSQueryRequest(SUFFIX="file server service",QUESTION_NAME=query_name, QUESTION_TYPE='NB')
        send (pkt, verbose=0)
        time.sleep(SLEEP_TIME)

# Handler for incoming NBNS responses
def get_packet(pkt):
    if not pkt.getlayer(NBNSQueryRequest):
        return
    if pkt.FLAGS == 0x8500:
        # Get the machine name from the NBNS response
        response_name = str(pkt.getlayer(NBNSQueryRequest).QUESTION_NAME).split("'")[1].rstrip()
        print(f'A spoofed NBNS response for {response_name} was detected by from host {pkt.getlayer(IP).src} - {pkt.getlayer(Ether).src}')

#Function for starting sniffing
def listen():
    sniff(filter="udp and port 137",store=0,prn=get_packet)

# Main function
def main():
    try:
        try:
            print ("Starting UDP Response Server...")
            threading.Thread(target=listen).start()
            print ("Starting NBNS Request Thread...")
            threading.Thread(target=sender).start()
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