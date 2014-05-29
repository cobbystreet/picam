#!/usr/bin/env bash

umask 000

PIDFILE="/home/pi/.picam/camserver.pid"
LOGDIR="/var/log/picam/"
CAMLOG="${LOGDIR}camserver.txt"
FTPLOG="${LOGDIR}ftpsync.txt"

DATE=`date`

#Check whether there is a previous ftpsync still running. Start or log otherwise.
if ! (ps xaf | grep "[/]ftpsync.sh" >/dev/null) ; then
  echo "${DATE} FTP Sync job starting" >>${FTPLOG}
  /var/www/cgi-bin/ftpsync.sh >>${FTPLOG} 2>&1
else
  echo "${DATE} FTP Sync job still running."
fi

#Check for running camServer
if [ -e "${PIDFILE}" ] && (ps xaf | grep "[ ]$(cat ${PIDFILE})[ ]" >/dev/null); then
#  echo "Already running."
  #If a reload has been issued from the web server (reload file touched) send a USR1 signal to the
  #running camServer
  if [[ "/var/lib/picam/reload" -nt "${PIDFILE}" ]] ; then
    echo "${DATE} issuing config reload"
    kill -SIGUSR1 $(cat ${PIDFILE})
    touch "${PIDFILE}"
  fi
  # A running camServer.py is the normal state. So exit normally
  exit 0
fi

#Save previous log file
#if [ -e "${CAMLOG}" ] ; then
#  mv "${CAMLOG}" "${CAMLOG}".old
#fi

echo "${DATE} Restarting camServer"
/usr/bin/python /var/www/cgi-bin/camServer.py >>"${CAMLOG}" 2>&1 &

echo $! > "${PIDFILE}"
chmod 644 "${PIDFILE}"


# Exit with notification
exit 1
