# Import packages
import os
import logger
import nbns
import llmnr
import mdns
import port_scan
import emailer
import alert_handler

logger.info("Starting up")

# Initialize the alert handler
alert_handler.init()

# If enabled send a test email at program startup
if str(os.environ['ENABLE_EMAIL_STARTUP_TEST']).lower()[0] == 't':
    logger.debug("Attempting to send startup test email...")
    if emailer.send_email("CanaryPi startup", "CanaryPi is starting up.  Your email settings have been configured correctly.") == False:
        logger.critical("Startup email attempt failed.  Killing program.")
        exit(1)

# If enabled start netbios spoof detection
if str(os.environ['DISABLE_NBNS_SCANNING']).lower()[0] != 't':
    nbns.init()

# If enabled start llmnr spoof detection
if str(os.environ['DISABLE_LLMNR_SCANNING']).lower()[0] != 't':
    llmnr.init()

# If enabled start mdns spoof detection
if str(os.environ['DISABLE_MDNS_SCANNING']).lower()[0] != 't':
    mdns.init()

# If enabled start port scan detection
if str(os.environ['DISABLE_PORTSCAN_DETECTION']).lower()[0] != 't':
    port_scan.init()