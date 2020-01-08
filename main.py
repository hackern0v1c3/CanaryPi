# Import packages
import logger
import nbns
import llmnr

logger.info("Starting up")
nbns.init()
llmnr.init()