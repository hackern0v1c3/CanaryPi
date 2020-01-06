# CanaryPi
Startup project to create a simple to deploy honey pot style detection tool for alerting on common network attacks

# Requirements
This container requires the --net=host option when starting.  At the time of writing this that option is only supported in linux so this container will not work on Windows or Mac Os hosts.  This is because the scripts need to send broadcast packets to the host network.

# Plan
I'm hoping to take some pre-existing tools and techniques for detecting common network attacks, like responder and port scanning, and package them in an easy to deploy tool.  I'm hoping this will help small IT teams that can't afford fancy security tools detect attacks on their network.

# Credit
I am building on the shoulders of giants.  Lots of credit to these guys who I 'borrowed' a lot of code from
[SpoofSpotter](https://github.com/NetSPI/SpoofSpotter)