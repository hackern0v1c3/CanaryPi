# Import modules
import os
import smtplib
import logger

# Function to check all required params
def check_params():
    if os.environ['EMAIL_RECIPIENT'] == '':
        logger.error("You must specify an email recipient for email alerts")
        return False
    if os.environ['EMAIL_SENDER'] == '':
        logger.error("You must specify an email address for sending email alerts")
        return False
    if os.environ['EMAIL_SERVER_ADDRESS'] == '':
        logger.error("You must specify an email server address for sending email alerts")
        return False
    if os.environ['EMAIL_SERVER_PORT'] == '':
        logger.error("You must specify an email server port for sending email alerts")
        return False
    try:
        int(os.environ['EMAIL_SERVER_PORT'])
    except:
        logger.error("Invalid email server port.  Must be int")
        return False
    logger.debug("Email params verified.")
    return True

# Funtion to send messag via email
def send_email(subject, message):
    if str(os.environ['ENABLE_EMAIL_ALERTS']).lower()[0] == 't':
        if check_params():
            server = smtplib.SMTP(os.environ['EMAIL_SERVER_ADDRESS'], int(os.environ['EMAIL_SERVER_PORT']))
            server.ehlo()

            if str(os.environ['EMAIL_SERVER_STARTTLS']).lower()[0] == 't':
                try:
                    server.starttls()
                except smtplib.SMTPHeloError:
                    logger.error('Error sending mail: The server didn’t reply properly to the HELO greeting.')
                    server.quit()
                    return
                except smtplib.SMTPNotSupportedError:
                    logger.error('The server does not support the STARTTLS extension.')
                    server.quit()
                    return
                except RuntimeError:
                    logger.error('SSL/TLS support is not available to your Python interpreter.')
                    server.quit()
                    return
                    
            if str(os.environ['ENABLE_EMAIL_SERVER_AUTHENTICATION']).lower()[0] == 't':
                try:
                    server.login(os.environ['EMAIL_SENDER'], os.environ['EMAIL_SENDER_PASSWORD'])
                except smtplib.SMTPHeloError:
                    logger.error('Error sending mail: The server didn’t reply properly to the HELO greeting.')
                    server.quit()
                    return
                except smtplib.SMTPAuthenticationError:
                    logger.error('Error sending mail: Credentials refused.')
                    server.quit()
                    return
                except smtplib.SMTPNotSupportedError:
                    logger.error('Error sending mail: The AUTH command is not supported by the server.')
                    server.quit()
                    return
                except smtplib.SMTPException:
                    logger.error('Error sending mail: No suitable authentication method was found.')
                    server.quit()
                    return

            body = '\r\n'.join(['To: %s' % os.environ['EMAIL_RECIPIENT'],
                    'From: %s' % os.environ['EMAIL_SENDER'],
                    'Subject: %s' % subject,
                    '', message])

            try:
                server.sendmail(os.environ['EMAIL_SENDER'], os.environ['EMAIL_RECIPIENT'], body)
                logger.info('Email sent')
            except smtplib.SMTPRecipientsRefused:
                logger.error('Error sending mail: Email recipients refused.')
            except smtplib.SMTPHeloError:
                logger.error('Error sending mail: Server did not respond to HELO greeting.')
            except smtplib.SMTPSenderRefused:
                logger.error('Error sending mail: The sender address was refused.')
            except smtplib.SMTPDataError:
                logger.error('Error sending mail: The server replied with an unexpected error code.')

            server.quit()
    else:
        logger.debug('Email alerts are disabled')