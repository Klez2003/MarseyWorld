#!/bin/bash

LOG='/var/log/rdrama/cron.log'

echo -e "\n---------------------------------------- $1 === $(date)" >> "$LOG"

source /e
. .env
/usr/local/bin/flask cron $1 >> "$LOG" 2>&1

echo -e "======================================== $1 === $(date)" >> "$LOG"
