FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt -y update
RUN apt -y upgrade
RUN apt -y autoremove
RUN apt install -y software-properties-common
RUN apt install -y sudo
RUN apt install -y supervisor
RUN apt install -y python3-pip
RUN apt install -y ffmpeg
RUN apt install -y postgresql
RUN apt install -y libpq-dev
RUN apt install -y nano
RUN apt install -y mailutils
RUN apt install -y exiv2

COPY requirements.txt /requirements.txt
COPY scripts/startup_docker_chat.sh /s

RUN pip3 install -r /requirements.txt

RUN mkdir /images
RUN mkdir /chat_images
RUN mkdir /songs
RUN mkdir /temp_songs
RUN mkdir /videos
RUN mkdir /audio
RUN mkdir /asset_submissions
RUN mkdir /asset_submissions/art
RUN mkdir /asset_submissions/emojis
RUN mkdir /asset_submissions/hats
RUN mkdir /asset_submissions/art/original
RUN mkdir /asset_submissions/emojis/original
RUN mkdir /asset_submissions/hats/original
RUN mkdir /var/log/rdrama

RUN apt install -y nginx
RUN rm /etc/nginx/sites-available -r
RUN rm /etc/nginx/sites-enabled/default
RUN mkdir /etc/nginx/includes

RUN apt install -y wget
RUN apt -y update
RUN apt upgrade -y cmake
RUN t=$(mktemp) && wget 'https://dist.1-2.dev/imei.sh' -qO "$t" && bash "$t" && rm "$t"

EXPOSE 80/tcp

RUN ln -sf /bin/bash /bin/sh

CMD [ "/usr/bin/supervisord", "-c", "/d/supervisord.conf" ]
