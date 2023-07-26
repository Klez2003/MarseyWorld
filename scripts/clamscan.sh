LOGFILE="/var/log/clamav/clamav-$(date +'%Y-%m-%d').log";

clamscan -ri --detect-pua=yes --exclude-dir=/sys/* / >> "$LOGFILE";

tail "$LOGFILE"|grep Infected|cut -d" " -f3
