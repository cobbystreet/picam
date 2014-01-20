#!/bin/bash
echo -e "Content-type: text/plain\n\n"

umask 000

LOGFILE=/var/log/picam/clonesd.txt
if ! (ps xa | grep '[/]clonesd.sh' >/dev/null ) ; then
  sudo stdbuf -o 0 /var/www/cgi-bin/clonesd.sh >${LOGFILE} 2>&1 &
fi

cat ${LOGFILE}
while (ps xa | grep '[/]clonesd.sh' >/dev/null ) ; do
  sudo killall -SIGUSR1 dd 
  tail -n 3 ${LOGFILE}
  sleep 2
done


