#!/bin/bash
#Run config.py (note the backticks). This returns the configuration as environment variables
eval `/var/www/cgi-bin/config.py`

FTPURL="ftp://$FTPUser:$FTPPass@$FTPHost"
#Save a link to the config page to "ip.html". This will be copied along with the images
LCD="/var/lib/picam/images"
cat <<HERE  >${LCD}/ip_${HOSTNAME}.html
<html>
<body>
$HOSTNAME is 
HERE
/sbin/ifconfig | awk 'BEGIN{FS="[: ]+";OFS=""}/inet addr/{print "<a href=\"http://",$4,"\">here</a>"}'>>${LCD}/ip_${HOSTNAME}.html
cat <<HERE  >>${LCD}/ip_${HOSTNAME}.html
</body>
</html>
HERE
#exit
#DELETE=--Remove-source-files

if [[ "${FTPPassive}" == "0" ]] ; then
  PASSIVEMODE="set ftp:passive-mode no"
fi
if [[ "${FTPUseCache}" == "1" ]] ; then
  USECACHE=" --use-cache "
fi
#Connect to server and mirror
lftp -q -c "set ftp:list-options -a;${PASSIVEMODE}
open '$FTPURL';
lcd $LCD;
mkdir -p $FTPPath;
cd $FTPPath;
set -a
mirror --reverse \
       --Remove-source-files ${USECACHE}\
       --verbose=2"
# \
#       --exclude-glob a-dir-to-exclude/ \
#       --exclude-glob a-file-to-exclude \
#       --exclude-glob a-file-group-to-exclude* \
#       --exclude-glob other-files-to-exclude"
