FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt -y update && \
    apt -y upgrade && \
    apt -y autoremove

RUN apt install -y software-properties-common \
                   sudo \
                   supervisor \
                   python3-pip \
                   ffmpeg \
                   postgresql \
                   libpq-dev \
                   nano \
                   mailutils \
                   nginx \
                   wget \
                   cmake

RUN t=$(mktemp) && wget 'https://dist.1-2.dev/imei.sh' -qO "$t" && bash "$t" && rm "$t"

COPY requirements.txt /requirements.txt
COPY scripts/startup_docker_chat.sh /s

RUN pip3 install -r /requirements.txt

RUN mkdir /images && \
    mkdir /chat_images && \ 
    mkdir /dm_media && \
    mkdir /songs && \
    mkdir /temp_songs && \
    mkdir /videos && \
    mkdir /audio && \
    mkdir /asset_submissions && \
    mkdir /asset_submissions/emojis && \
    mkdir /asset_submissions/hats && \
    mkdir /asset_submissions/emojis/original && \
    mkdir /asset_submissions/hats/original && \
    mkdir /var/log/rdrama

RUN rm /etc/nginx/sites-available -r && \
    rm /etc/nginx/sites-enabled/default && \
    mkdir /etc/nginx/includes

EXPOSE 80/tcp

CMD [ "/usr/bin/supervisord", "-c", "/d/supervisord.conf" ]
