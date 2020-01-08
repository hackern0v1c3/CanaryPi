FROM python:3

ARG BROADCAST_IP=''
ENV BROADCAST_IP="${BROADCAST_IP}"
ARG NBNS_SLEEP=30
ENV NBNS_SLEEP="${NBNS_SLEEP}"
ARG LLMNR_SLEEP=30
ENV LLMNR_SLEEP="${LLMNR_SLEEP}"


RUN apt-get update && apt-get install -y --no-install-recommends tcpdump && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./nbns.py" ]