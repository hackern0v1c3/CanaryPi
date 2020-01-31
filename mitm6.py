# Test script for detecting mitm6 spoofing

# Import modules
from scapy.all import *
import threading
import random
import string
#import logger
#import alert_handler
from netaddr import *

import codecs
decode_hex = codecs.getdecoder("hex_codec")

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

mac_pieces = generate_mac_pieces()

mac_address = (':').join(mac_pieces)

# Generate interface ID in EUI-64 format
# https://networklessons.com/ipv6/ipv6-eui-64-explained
eui64 = mac_pieces[0] + mac_pieces[1] + ":" + mac_pieces[2] + "ff" + ":" + "fe" + mac_pieces[3] + ":" + mac_pieces[4] + mac_pieces[5]

""" Generates Link-local  IPv6 addres in EUI-64 format"""
ip6_ll_eui64 = "fe80" + "::" + eui64





# Building and initilizing DHCP SOLICIT packet layers with common parameters
l2 = Ether()
l3 = IPv6()
l4 = UDP()
sol = DHCP6_Solicit()
rc = DHCP6OptRapidCommit()
opreq = DHCP6OptOptReq()
et= DHCP6OptElapsedTime()
cid = DHCP6OptClientId()
iana = DHCP6OptIA_NA()
rc.optlen = 0
opreq.optlen = 4
iana.optlen = 12
iana.T1 = 0
iana.T2 = 0
cid.optlen = 10
# macdst = "ca:00:39:b8:00:06"
# l2.dst = macdst
l3.dst = "ff02::1:2"
l4.sport = 546
l4.dport = 547





# Generating MAC and its corresponding IPv6 link-local in EUI-64 format

#macsrc = macs.form1b()
macsrc = mac_address

#ipv6llsrc = macs.ip6_ll_eui64()
ipv6llsrc = ip6_ll_eui64

# Initializaing the source addreses
l2.src = macsrc
l3.src = ipv6llsrc

random.seed()
# Generating SOLICIT message id
sol.trid = random.randint(0,16777215)

# Generating DUID-LL
#####cid.duid = ("00030001"+ str(EUI(macsrc)).replace("-","")).encode().decode("hex")
#print("00030001"+str(EUI(macsrc)).replace("-",""))
#print(decode_hex("00030001"+str(EUI(macsrc)).replace("-",""))[0])
cid.duid = (decode_hex("00030001"+str(EUI(macsrc)).replace("-",""))[0])

# Assembing the packet
pkt = l2/l3/l4/sol/iana/rc/et/cid/opreq

# GO!
#sendp(pkt, iface='eth1')
sendp(pkt)
#send (pkt, verbose=0)
