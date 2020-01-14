# Import modules
import logger
import emailer
import os
import threading
import time
# Regex pattern for only stripping special characters from string
import re; pattern = re.compile('[\W_]+')
from datetime import datetime

# List to hold alerts in memory before writing them to disk
new_alerts = []
attack_duration = 0

# Function for accepting new alert messages from other modules
def new_alert(attack_type, source_ip, source_mac, message):
    alert_info = [attack_type, source_ip, pattern.sub('', source_mac), message]
    logger.debug(f'new alert received by handler {alert_info}')
    new_alerts.append(alert_info)

# Function for starting mail worked loop
def work():
    # Make sure the attack duration value is valid
    try:
        attack_duration = int(os.environ['ATTACK_TIMEOUT_DURATION'])
        logger.debug(f'Attack duration timeout set to {attack_duration}')
    except:
        logger.error("Invalid value for Attack Timeout Duration.  Must be int")
        exit(1)

    logger.debug('Starting alert handler worker thread')

    # Make sure queue folder exists
    root = os.getcwd()
    attack_file_path = os.path.join(root, 'attacks')
    os.makedirs(attack_file_path,exist_ok=True)

    # Setup list to track which attacks have been alerted on
    alerted = []

    while 1:
        # Get all existing file names for detected attacks
        existing_attack_files = []

        logger.debug('Fetching current attack file names')
        with os.scandir(attack_file_path) as file_names:
            for file_name in file_names:
                if file_name.is_file():
                    existing_attack_files.append(file_name.name)

                    # If any notifications haven't been sent for an attack file send it.
                    if file_name.name not in alerted:
                        attack_info = file_name.name.split('_')
                        logger.debug('Sending notification email for new attack')
                        email_body = f'{attack_info[0]} attack detected from ip {attack_info[1]} mac {attack_info[2]}\n'
                        email_body += f'See CanaryPi logs for more detail.'

                        if emailer.send_email("CanaryPi Attack Detected", email_body):
                            alerted.append(file_name.name)

        for _ in range(len(new_alerts)):
            # Grab the most recent alert out of the new_alerts list
            alert = new_alerts.pop()

            # Grab the message from the alert
            message = alert.pop()

            # Combine the attack type, source ip, and source mac into a name
            attacker_ip = alert[1]
            attacker_mac = alert[2]
            alert_name = "_".join(alert)
            attack_file_name = os.path.join(attack_file_path, alert_name)

            # If new attack_type, source_ip or source_mac then create temporary attack file
            if alert_name not in existing_attack_files:
                logger.debug('Writing new attack file')
                with open(attack_file_name, 'w') as f:
                    f.write(f'{datetime.now().strftime("%Y/%m/%d %H:%M:%S")} - {message} from ip {attacker_ip} mac {attacker_mac}\n')
                    existing_attack_files.append(alert_name)

                    logger.debug('Sending notification email for new attack')
                    email_body = f'Attack detected from ip {attacker_ip} mac {attacker_mac}\n'
                    email_body += f'{message}'

                    if emailer.send_email("CanaryPi Attack Detected", email_body):
                        alerted.append(alert_name)

            # Otherwise append to the existing one.
            else:
                logger.debug('Appending to attack file')
                with open(attack_file_name, 'a') as f:
                    f.write(f'{datetime.now().strftime("%Y/%m/%d %H:%M:%S")} - {message} from ip {alert[1]} mac {alert[2]}\n')

        # for each on disk que get the last written to time/date
        with os.scandir(attack_file_path) as file_names:
            for file_name in file_names:
                if file_name.is_file():
                    # compare most recent activity to attack timeout time
                    current_time = time.time()
                    modified_time = os.path.getmtime(file_name)
                    time_since_modified = current_time - modified_time

                    # if time has expired
                    if time_since_modified > attack_duration:
                        # Read file from disk and build summary
                        with open(file_name, 'r') as f:
                            lines = f.readlines()

                        line_parts = lines[0].split("-", 1)
                        start_time = line_parts[0]
                        end_time = lines[len(lines) - 1].split("-")[0]
                        attack_details = line_parts[1].split(" ")
                        attack_type = attack_details[1]
                        attacker_ip = attack_details[7]
                        attacker_mac = attack_details[9]

                        # Build email message
                        message =f'{attack_type} attack has not been detected for {attack_duration} seconds from ip {attacker_ip}, mac {attacker_mac}'
                        message +=f'Considered over.  See details below\n'
                        message +=f'The attack began at {start_time} and ended at {end_time}\n'
                        message +=f'There were {str(len(lines))} instances of this attack detected during that timeframe.\n'
                        message +=f'For more information see the CanaryPi log files\n'

                        # Send email alert with summary
                        logger.debug(f'Sending email because attack is considered over {str(time_since_modified)} is greater than {attack_duration}')
                        if emailer.send_email("CanaryPi Attack Ended", message):
                            # Delete file from disk
                            os.remove(file_name)

                            # Remove item from alerted list
                            alerted.remove(file_name.name)

        # sleep x seconds
        # remember this is hard coded
        logger.debug('Alert worker sleeping')
        time.sleep(10)

def init():
    logger.debug('Starting alert handler')

    threading.Thread(target=work).start()