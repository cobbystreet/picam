#!/usr/bin/python
import datetime
import sys

#Initial config loading
import config
config.load()

#Signal handler. startserver.sh sends a USR1 signal to trigger config reloading
import signal
def sigUSR1_handler(signal, frame):
  print "Reloading Config file"
  config.load()

#Install signal handler
signal.signal(signal.SIGUSR1, sigUSR1_handler)


import time
import takePhoto
print datetime.datetime.today().isoformat()+" CamServer starting"

while True:
  now=datetime.datetime.today()
  diff=now-config.values['starttime'][0]
  if (config.values['starttime'][0].time()<=now.time()) and (config.values['endtime'][0].time()>now.time()):
    #This has been disabled because it causes issues if taking photos takes longer than a second
    #Interval timing is taken care of accurately below.
##    if (diff.seconds % config.values['interval'][0]==0):
    FN=takePhoto.takePhoto(config,now)
    if (FN==None):
      print "Failed to acquire image. Exiting."
      sys.exit(-1)
    print "wrote image "+now.strftime(config.values['FNpattern'][0])

  #Take the difference of "now" and "starttime" from above and increase it by one interval period
  diff=datetime.timedelta(diff.days,(diff.seconds/config.values['interval'][0]+1)*config.values['interval'][0])
  #Add the increased difference to the current time
  delta=(config.values['starttime'][0]+diff-datetime.datetime.today())
  #Sleep for the prescribed time
  time.sleep(delta.seconds+delta.microseconds*1e-6)

