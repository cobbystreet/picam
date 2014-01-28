#!/usr/bin/python
#calling external processes
import subprocess

#web browser IO
import cgitb
cgitb.enable()
import cgi
#load all data supplied as results with button presses
form = cgi.FieldStorage()

#load camServer config from XML file
import config
config.load()


#A Content type needs to be set for all web browser output. Note the TWO line feeds!
print "Content-type: text/html\n\n"
print '<html><head><script>\
function loadTestImg(){document.getElementById("TESTIMG").src = "/cgi-bin/takePhoto.py?" + new Date().getTime();}\
</script></head><body>'
import platform

print "<h2>Web config for "+platform.node()+"</h2>"

if ('wpa' in form) and (form['wpa'].value=='Change WPA Settings'):
  #write the entire content of the WPA config textarea into wpa_supplicant.conf verbatim
  #wpa_supplicant.conf needs to be writable by www-data user
  #chown root.picam /etc/wpa_supplicant/wpa_supplicant.conf
  #chmod g+rw /etc/wpa_supplicant/wpa_supplicant.conf
  wpaconf=open("/etc/wpa_supplicant/wpa_supplicant.conf","w")
  wpaconf.write(form['wpaconf'].value)
  wpaconf.close()
  print "<BR>WPA Settings saved."
  #www-data needs to be allowed to call the networkfallback script to restart
  #insert
  #www-data ALL=(ALL) NOPASSWD: /usr/sbin/service networkfallback start
  #www-data ALL=(ALL) NOPASSWD: /usr/sbin/service networkfallback stop
  #into /etc/sudoers
  p=subprocess.Popen("sudo service networkfallback stop; sudo service networkfallback start",shell=True)
  

print '<form method="get" action="/cgi-bin/webConfig.py">'

def writeConf(k):
  #For a value named k, print a field with its contents plus description
  #Parsing of new values is done here as well. See config.py for details
  inputstring='<BR><input type="text" name="'+k+'" value="'
  if k in form:
    inputstring+=form[k].value+'"/><span '
    try:
      #Apply the conversion function (index 2 in values array) to the form value and save the result
      config.values[k][0]=config.values[k][2](form[k].value)
    except:
      #Print the description string in Red for errors
      inputstring+='style="color:#FF0000"'
  else:
    #Apply the back conversion (index 3) to the saved value (index 0)
    inputstring+=config.values[k][3](config.values[k][0])+'"/><span '
  print inputstring+'>'+config.values[k][1]+'</span>'

#Here come the settings.
#They could easily be iterated over automatically with "for k in config.values.keys()"
#But that results in an unordered list with no extra comments or sectioning.
print '<TABLE><TR><TD>'
print "<BR><B>Frame Settings:</B>"
for k in ['FrameWidth','FrameHeight']:
  writeConf(k)
p=subprocess.Popen("lsusb -v | awk 'BEGIN{ORS=\"\"}/Width/{print $0}/Height/{print $0,\"\\n\"}' | sort -n -k 2 | tail -n 1",shell=True,\
  stdout=subprocess.PIPE)
output=p.communicate()[0]
print "<BR>(maximum for PiCam is 2592x1944, WebCam Resolution: "+output+")"
print '<BR><input id="clickMe" type="button" value="Test Image Capture" onclick="loadTestImg();" />'
print '</TD><TD><IMG WIDTH="640" HEIGHT="480" ID="TESTIMG" ALT="Test Image"></TD></TR></TABLE>'
print "<HR><B>Time Lapse Settings:</B><BR>If Interval is less than 60 seconds, the Filename Pattern must be unique (otherwise it will be overwritten between FTP uploads)."
for k in ['interval','starttime','endtime','FNpattern']:
  writeConf(k)
print "<HR><B>FTP Settings:</B><BR>FTP uploads happen asynchronously from photography once per minute."
for k in ['FTPHost','FTPUser','FTPPass','FTPPath','FTPPassive']:
  writeConf(k)
print '<HR><B>SDCard Cloning Settings:</B><BR>Set these and then start the clonescript "doclone.sh"'
for k in ['CloneHost','CloneDev']:
  writeConf(k)
print '<br>Last Clone stat:<br><pre>'
try:
  clonelog=open("/var/log/picam/clonesd.txt","r")
  print clonelog.read()[-300:]
  clonelog.close()
except IOError:
  print "Can't read clonesd.txt. Empty or Permissions problem?"
print '</pre>'
print '<br><input type="submit" name="settings" value="Commit Changes"/>Changes will be saved immediately, and transfered to Camera Server on next WatchDog check (once a minute)</br>'
print '</form><br>'
#End of settings button

#Test Button. This needn't be a form really...
print '<form method="get" action="/cgi-bin/webConfig.py">'
print '<input type="submit" name="ftptest" value="Test"/>(Remember to commit changes first!!)<br>This will take a photo and upload it to the FTP server. The photo will be displayed in the browser window as well.'
print '</form><br>'

#WPA supplicant form.
print '<form method="get" action="/cgi-bin/webConfig.py">'
print '<textarea name="wpaconf" rows="10" cols="50">'
try:
  wpaconf=open("/etc/wpa_supplicant/wpa_supplicant.conf","r")
  print wpaconf.read()
  wpaconf.close()
except:
  print "Can't read /etc/wpa_supplicant/wpa_supplicant.conf. Permissions problem?"
print '</textarea>'
print '<input type="submit" name="wpa" value="Change WPA Settings"/>'
print '</form><br>'

#Print links to log files
print 'Download <a href="/log/camserver.txt">Camera Log</a>(<a href="/log/camsever.txt.old">previous</a>) <a href="/log/ftpsync.txt">FTP Log</a> <a href="/log/startserver.txt">WatchDog Log</a> <a href="/cgi-bin/picam.tgz">All Source tgz</a> <a href="/config.xml">config.xml</a>'

#Test button was pressed. Take a photo, call the ftpsync script and time the result
if ('ftptest' in form) and (form['ftptest'].value=='Test'):
  import takePhoto
  import datetime
  print "<BR>Capturing Photo:<BR><PRE>"
  before=datetime.datetime.today()
  FN=takePhoto.takePhoto(config)
  photoTime=datetime.datetime.today()
  import os
  print '</PRE><IMG SRC="/current.jpg"><BR>Time: ',str(photoTime-before)
  #Call ftpsync as sub-process. Capture output with pipes to return to the user.
  p=subprocess.Popen("/var/www/cgi-bin/ftpsync.sh",shell=True,\
    stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  output,error=p.communicate()
  ftpTime=datetime.datetime.today()
  print "<BR>FTP upload:<BR>Output:<PRE>"+output+"</PRE>Error:<PRE>"+error+"</PRE>"
  print "Time: ",str(ftpTime-photoTime),"<BR>Total Time:",str(ftpTime-before)

if ('settings' in form) and (form['settings'].value=='Commit Changes'):
  #Save the config.
  if config.save():
    #Opening the reload file allows the cronjob WatchDog to issue a config reload in the camServer
    reloadFile=open(config.campath+'reload','w')
    print >>reloadFile,"1"
    reloadFile.close()
    print "<BR>Settings saved and camServer reload initiated."
print "</body></html>"

