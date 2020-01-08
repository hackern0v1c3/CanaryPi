FROM python:3

ARG BROADCAST_IP=''
ENV BROADCAST_IP="${BROADCAST_IP}"
ARG NBNS_SLEEP=30
ENV NBNS_SLEEP="${NBNS_SLEEP}"
ARG LLMNR_SLEEP=30
ENV LLMNR_SLEEP="${LLMNR_SLEEP}"
ARG CONSOLE_LOG_LEVEL="warning"
ENV CONSOLE_LOG_LEVEL="${CONSOLE_LOG_LEVEL}"
ARG FILE_LOG_LEVEL="warning"
ENV FILE_LOG_LEVEL="${FILE_LOG_LEVEL}"
ARG FILE_LOG_RETENTION=30
ENV FILE_LOG_RETENTION="${FILE_LOG_RETENTION}"

RUN apt-get update && apt-get install -y --no-install-recommends tcpdump && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
VOLUME [ "/usr/src/app/logs" ]

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]