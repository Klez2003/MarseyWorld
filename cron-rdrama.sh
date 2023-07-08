#!/bin/bash

LOG='/var/log/rdrama/cron.log'

echo -e "\n======================================== $1 === $(date --iso-8601=minutes)" >> "$LOG"

source .env
/usr/local/bin/flask cron $1 >>"$LOG" 2>&1
