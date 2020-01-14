# CanaryPi
Startup project to create a simple to deploy honey pot style detection tool for alerting on common network attacks.  This is currently and early alpha build used for public testing and feedback while it's further developed.

# Requirements
This container requires the --net=host option when starting.  At the time of writing this that option is only supported in linux so this container will not work on Windows or Mac Os hosts.  This is because the scripts need to send broadcast packets to the host network.  The docker container is cross compiled using buildx so canarypi should be able to run on x86 or arm machines.

# Plan
I'm hoping to take some pre-existing tools and techniques for detecting common network attacks, like responder and port scanning, and package them in an easy to deploy tool.  I'm hoping this will help small IT teams that can't afford fancy security tools detect attacks on their network.

# Current Features
Currently the following attacks can be detected on a network
1. NBNS spoofing.  Typically from [Responder](https://github.com/lgandx/Responder)
2. LLMNR spoofing. Typically from [Responder](https://github.com/lgandx/Responder)

The next attacks that I plan on adding detection for are
1. mDNS spooging. Typically from [Responder](https://github.com/lgandx/Responder)
2. Port scanning. Typically from [NMap](https://github.com/nmap/nmap)

If there are other network based attacks that you would like to see me add support for please feel free to reachout by opening an issue or pull request.

# Instructions
## Quickstart
If you just want to get up and running quickly you can use the following command.  With the defaults you will receive a test email when the program starts up.  Then you will receive an email each time a new attack is detected.  By default if a particular attack hasn't been detected for 1 hour it is considered over and you will receive a summay email.  If you didn't specify that you do NOT want a startup email but you still didn't receive it there is likely something wrong with the email info you provided.  The log canarypi log file should contain some information on what went wrong.

If you use the quickstart command below the logs will be located in /var/lib/docker/volumes/canary_logs/_data/.  These will contain a more detail history of the attacks that can be used for forensics.

The other volume /var/lib/docker/volumes/canary_logs/_data/ is just used for temporary files where attack info is stored during an attack.  When the attack is over the files in this folder are read into a summary and then delted.  You should use the logs, not these files, to look up attack history info.

Note all times reported by Canarypi are currently in UTC

```
docker run -dit --net=host \
--restart unless-stopped \
-e EMAIL_SENDER='address used to send alert emails' \
-e EMAIL_SENDER_PASSWORD='password for account used to send emails' \
-e EMAIL_RECIPIENT='address to receive alert emails' \
-v canary_logs:/usr/src/app/logs \
-v canary_attacks:/usr/src/app/attacks \
macmondev/canarypi:latest
```

## Advanced Usage
There are a lot of optional params that can be passed to the container.  Any of the following params can be added to the docker startup command using 

```-e paramname='paramvalue'```  

For instance adding this would disable NBNS spoof detection

```-e DISABLE_NBNS_SCANNING='True'```

You don't need to wrap all of the param values in single quotes but it's a good idea, especially if the values contain special characters.

### Detection Related Parameters
#### NBNS Params
| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
|DISABLE_NBNS_SCANNING|False|False|Set to True if you do not want to try and detect NBNS spoofing|
|BROADCAST_IP|False|224.0.0.252|By default this program will send nbns requests to the multicast address 224.0.0.252 which is not protocol compliant but has worked in testing.  For better detection set this value to the actual broadcast address of your network.  Like 192.168.1.255|
|NBNS_SLEEP|False|30|Determines how ofter the network is checked for NBNS spoofing|

#### LLMNR Params
| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
|DISABLE_LLMNR_SCANNING|False|False|Set to True if you do not want to try and detect LLMNR spoofing|
|LLMNR_SLEEP|False|30|Determines how ofter the network is checked for LLMNR spoofing|

#### Logging Related Params
| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
|CONSOLE_LOG_LEVEL|False|warning|Set the docker console logging level.  Supported values are debug, info, warning, error, and critical.  At least warning must be set to report on detected attacks|
|FILE_LOG_LEVEL|False|warning|Set logging level for the log files.  Supported values are debug, info, warning, error, and critical.  At least warning must be set to report on detected attacks|
|FILE_LOG_RETENTION|False|30|How many days of rotating log files to keep|
|SYSLOG_ENABLED|False|False|Set to true to enable syslog logging|
|SYSLOG_ADDRESS|False|null|The ip address of the syslog server.  Required if SYSLOG_ENABLED is True|
|SYSLOG_PORT|False|514|The port that the syslog server is listening on|
|SYSLOG_TCP|False|False|Set to false for UDP syslog server or True for TCP syslog server|
|SYSLOG_LOG_LEVEL|False|warning|The level of logs to be sent to the syslog server.  Supported values are debug, info, warning, error, and critical.  At least warning must be set to report on detected attacks|

#### Email Related Parameters
| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
|ENABLE_EMAIL_ALERTS|False|True|If set to False the program wont attempt to send any emails|
|ENABLE_EMAIL_STARTUP_TEST|False|True|If set to False the program wont send an email on startup.|
|ENABLE_EMAIL_SERVER_AUTHENTICATION|False|True|If set to false the program wont attempt to login to the smtp server when sending emails.  Useful if using an anonymous relay.|
|EMAIL_SERVER_ADDRESS|False|smtp.gmail.com|The email server that the program will connect to for sending email notifications|
|EMAIL_SERVER_PORT|False|587|The smtp port for the email server used to send notications|
|EMAIL_SERVER_STARTTLS|False|True|Set to False if the email server does not require start tls.  Setting this to false sends your credentials in clear text and is considered insecure|
|EMAIL_RECIPIENT|False||The email address that will receive any email notifications.  Only equied if ENABLE_EMAIL_ALERTS is True|
|EMAIL_SENDER|False||The email address that will be used to send email notifications. Only requied if ENABLE_EMAIL_ALERTS is True|
|EMAIL_SENDER_PASSWORD|False||The password for the email address used to send email notifications.  Only requied if ENABLE_EMAIL_ALERTS is True and ENABLE_EMAIL_SERVER_AUTHENTICATION is set to True|


#### Misc Parameters
| Name | Required | Default Value | Description |
|------|----------|---------------|-------------|
|ATTACK_TIMEOUT_DURATION|False|3600|The ammount of innactivity time, in seconds, before an attack is considered over.  So by default if an attack was started, but hasn't been detected for over an hour, it is considered over.  You will be notified based on your logging and email settings.|

# Credit
I am building on the shoulders of giants.  Lots of credit to these guys who I 'borrowed' a lot of code from

[Scapy](https://scapy.net/)

[SpoofSpotter](https://github.com/NetSPI/SpoofSpotter)