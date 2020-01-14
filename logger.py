# Import packages
import os
import logging
import socket
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import SysLogHandler

# Make sure the log folder exists
os.makedirs('logs',exist_ok=True)

# Function to verify the logging levels provided were valid
def validate_log_level(level):
    if level == 'DEBUG':
        return True
    elif level == 'INFO':
        return True
    elif level == 'WARNING':
        return True
    elif level == 'ERROR':
        return True
    elif level == 'CRITICAL':
        return True
    else:
        return False

# Create loggers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_logger = logging.getLogger('Rotating Log by Day')
console_logger = logging.getLogger('Log to Console')
syslog_logger = logging.getLogger('Syslog')

# Verify a valid logging level was provided for console logging
console_log_level = str(os.environ['CONSOLE_LOG_LEVEL']).upper()
if validate_log_level(console_log_level):
    console_logger.setLevel(console_log_level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_logger.addHandler(console_handler)
else:
    print("Invalid log level provided for console logging.  Must be debug, info, warning, error, or critical")
    exit(1)

# Verify a valid logging level was provided for file logging
file_log_level = str(os.environ['FILE_LOG_LEVEL']).upper()
if validate_log_level(file_log_level):
    file_logger.setLevel(file_log_level)
else:
    console_logger.critical("Invalid log level provided for file logging.  Must be debug, info, warning, error, or critical")
    exit(1)

# Verify a valid logging level was provided for syslog logging
syslog_log_level = str(os.environ['SYSLOG_LOG_LEVEL']).upper()
if validate_log_level(syslog_log_level):
    syslog_logger.setLevel(syslog_log_level)
else:
    console_logger.critical("Invalid log level provided for syslog logging.  Must be debug, info, warning, error, or critical")
    exit(1)

# Setup file logging options
try:
    log_retention = int(os.environ['FILE_LOG_RETENTION'])
    file_handler = TimedRotatingFileHandler('logs/canary.log', when="d", interval=1,  backupCount=log_retention)
    file_handler.setFormatter(formatter)
    file_logger.addHandler(file_handler)
except:
    console_logger.critical("Invalid log retention provided.  Must be int")
    exit(1)

# Setup syslog logging options
if os.environ['SYSLOG_ENABLED'][0].lower() == 't':
    try:
        syslog_port = int(os.environ['SYSLOG_PORT'])
    except:
        console_logger.critical("Invalid syslog port provided.  Must be int")
        exit(1)

    if os.environ['SYSLOG_ADDRESS'] == '':
        console_logger.critical("You must provide an ip address for the syslog server")
        exit(1)

    syslog_server = os.environ['SYSLOG_ADDRESS']
    syslog_socktype = socket.SOCK_DGRAM

    # Check if using TCP for syslog
    if os.environ['SYSLOG_TCP'][0].lower() == 't':
        syslog_socktype = socket.SOCK_STREAM

    # Connections can fail if using TCP handler
    try:
        syslog_handler = SysLogHandler(address=(syslog_server, syslog_port), socktype=syslog_socktype)
    except:
        console_logger.critical("Unable to connect to syslog server")
        exit(1)

    syslog_handler.setFormatter(formatter)
    syslog_logger.addHandler(syslog_handler)

# Setup functions for easily logging to console, file, and syslog at the same time.
def debug(message):
    console_logger.debug(message)
    file_logger.debug(message)
    if os.environ['SYSLOG_ENABLED'][0].lower() == 't':
        syslog_logger.debug(message)

def info(message):
    console_logger.info(message)
    file_logger.info(message)
    if os.environ['SYSLOG_ENABLED'][0].lower() == 't':
        syslog_logger.info(message)

def warning(message):
    console_logger.warning(message)
    file_logger.warning(message)
    if os.environ['SYSLOG_ENABLED'][0].lower() == 't':
        syslog_logger.warning(message)

def error(message):
    console_logger.error(message)
    file_logger.error(message)
    if os.environ['SYSLOG_ENABLED'][0].lower() == 't':
        syslog_logger.error(message)

def critical(message):
    console_logger.critical(message)
    file_logger.critical(message)
    if os.environ['SYSLOG_ENABLED'][0].lower() == 't':
        syslog_logger.critical(message)
