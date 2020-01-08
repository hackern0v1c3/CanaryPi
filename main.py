# Import packages
import os
import logging
from logging.handlers import TimedRotatingFileHandler

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

# Setup file logging options
try:
    log_retention = int(os.environ['FILE_LOG_RETENTION'])
    file_handler = TimedRotatingFileHandler('logs/canary.log', when="d", interval=1,  backupCount=log_retention)
    file_handler.setFormatter(formatter)
    file_logger.addHandler(file_handler)
except:
    console_logger.critical("Invalid log retention provided.  Must be int")
    exit(1)