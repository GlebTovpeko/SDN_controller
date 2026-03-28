FROM python:3.10-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow

# Установка всех пакетов одной командой
# mininet берётся из репозитория Debian — никаких скриптов!
RUN apt-get update && apt-get install -y --no-install-recommends \
    mininet \
    openvswitch-switch \
    iperf3 \
    iproute2 \
    iputils-ping \
    net-tools \
    bridge-utils \
    tcpdump \
    curl \
    wget \
    sudo \
    && rm -rf /var/lib/apt/lists/* \
    && ldconfig

# Python зависимости
RUN pip install --no-cache-dir requests==2.31.0

WORKDIR /project

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]