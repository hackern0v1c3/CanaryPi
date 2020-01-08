# Import packages
import logger
import nbns
import llmnr

logger.info("Starting up")

if str(os.environ['DISABLE_NBNS_SCANNING']).lower()[0] != 't':
    nbns.init()
if str(os.environ['DISABLE_LLMNR_SCANNING']).lower()[0] != 't':
    llmnr.init()