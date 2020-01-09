# Import modules
import logger
import emailer
import os
import threading
import time
# Regex pattern for only stripping special characters from string
import re; pattern = re.compile('[\W_]+')

# List to hold alerts in memory before writing them to disk
new_alerts = []
attack_duration = 0

# Function for accepting new alert messages from other modules
def new_alert(attack_type, source_ip, source_mac, message):
    alert_info = [attack_type, pattern.sub('', source_ip), pattern.sub('', source_mac), message]
    logger.debug(f'new alert received by handler {alert_info}')
    new_alerts.append(alert_info)

# Function for starting mail worked loop
def work():
    logger.debug('Starting alert handler worker thread')

    # Make sure queue folder exists
    os.makedirs('attacks',exist_ok=True)

    while 1:
        # Get all existing file names for detected attacks
        existing_attack_files = []

        logger.debug('Fetching current attack file names')
        with os.scandir('/usr/src/app/attacks') as file_names:
            for file_name in file_names:
                if file_name.is_file():
                    existing_attack_files.append(file_name.name)

        for alert in new_alerts:
            # Grab the message from the alert
            message = alert.pop()

            # Combine the attack type, source ip, and source mac into a name
            alert_name = "_".join(alert)
            file_name = '/usr/src/app/attacks/' + alert_name

            # if new attack_type, source_ip or source_mac
            if alert_name not in existing_attack_files:
                logger.debug('Sending notification email for new attack')
                emailer.send_email("CanaryPi Attack Detected", message)

                logger.debug('Writing new attack file')
                with open(file_name, 'w') as f:
                    f.write(message + '\n')
            else:
                # append to existing on disk queue with message and timestamp
                logger.debug('Appending to attack file')
                with open(file_name, 'a') as f:
                    f.write(message + '\n')

        # empty in memory queue
        logger.debug('Clearing alert queue')
        new_alerts.clear()

        # for each on disk que get the last written to time/date
        with os.scandir('/usr/src/app/attacks') as file_names:
            for file_name in file_names:
                if file_name.is_file():
                    # compare most recent activity to attack timeout time
                    current_time = time.time()
                    modified_time = os.path.getmtime(file_name)
                    time_since_modified = current_time - modified_time
                    # if time has expired
                    if time_since_modified > int(os.environ['ATTACK_TIMEOUT_DURATION']):
                        duration = int(os.environ['ATTACK_TIMEOUT_DURATION'])
                        # Read file from disk and build summary
                        # send email alert with summary
                        # STILL NEED TO ADD SUMMARY
                        message = f'Attack has not been detected for {attack_duration} seconds.  Considered over.  See details below\n'
                        message +='There should totally be details here...'
                        #emailer.send_email("CanaryPi Attack Ended", message)
                        logger.debug(f'would email because {str(time_since_modified)} is greater than {duration}')
                        # Delete file from disk
        # sleep x seconds
        # remember this is hard coded
        logger.debug('Alert worker sleeping')
        time.sleep(30)

def init():
    logger.debug('Starting alert handler')
    try:
        attack_duration = int(os.environ['ATTACK_TIMEOUT_DURATION'])
        logger.debug(attack_duration)
    except:
        logger.error("Invalid value for Attack Timeout Duration.  Must be int")
        exit(1)

    threading.Thread(target=work).start()