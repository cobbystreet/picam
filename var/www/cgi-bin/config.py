#!/usr/bin/python
#import picam

import datetime
import os
os.umask (000)

import xml.etree.ElementTree as ET

timeFormat='%H:%M:%S'

def pathCheck(path):
  assert path==path.translate(None, '<>:"/\\|?*')
  return path

#Value storage for configuration. Saved to config.xml and read from web form.
#4 entries for each value:
#Default value in string form
#String description
#Conversion function FROM string to actual value
#Back-Conversion from saved value TO actual string

values={'interval':['10','Photo interval in seconds (integer)',lambda x:int(x),lambda x:str(x)],\
'FrameWidth':['640','Width of Capture Frame (integer)',lambda x:int(x),lambda x:str(x)],\
'FrameHeight':['480','Height of Capture Frame (integer)',lambda x:int(x),lambda x:str(x)],\
'starttime':['00:00:00','Start Time (Format '+timeFormat+', "00:00:00" to disable)',lambda x:datetime.datetime.strptime(x,timeFormat),lambda x:x.strftime(timeFormat)],\
'endtime':['23:59:59','End Time (Format '+timeFormat+', "23:59:59" to disable)',lambda x:datetime.datetime.strptime(x,timeFormat),lambda x:x.strftime(timeFormat)],
'FNpattern':['%Y-%m-%d_%H-%M-%S.jpg','Filename Pattern (using placeholders "%Y-%m-%d_%H-%M-%S.jpg" for time and date).<BR>Must obey filename conventions (offending characters: <>:"/\\|?*).',lambda x:pathCheck(x),lambda x:x],\
'FTPHost':['localhost','FTP Server Host Name (name or IP)',lambda x:x,lambda x:x],
'FTPUser':['picam','FTP Username',lambda x:x,lambda x:x],
'FTPPass':['thisispicam','FTP Password',lambda x:x,lambda x:x],
'FTPPassive':['0','Passive FTP mode (0 to disable, 1 to enable)',lambda x:x,lambda x:x],
'FTPUseCache':['0','Use FTP Directory Cache. May speed up the process considerably if many files are present in the upload dir. (0 to list, 1 to use cache)',lambda x:x,lambda x:x],
#'FTPOpts':['','FTP extra Options',lambda x:x,lambda x:x],
'FTPPath':['/home/picam/picam001','FTP Server Directory (example: "/data/upload", leading "/" indicates absolute directory on FTP server)',lambda x:x,lambda x:x],
'CloneDev':['/dev/sda','Device of SDCard reader to clone to (example "/dev/sda"). Use extreme caution when other storage devices are connected!!!',lambda x:x,lambda x:x],
'CloneHost':['picam002','Hostname (and ssid) of cloned picam. Should be unique',lambda x:x,lambda x:x],
}

def getVal(name,default=None):
  #Read a value from the config file and supply the default if it's missing in the file.
  try:
    return xml.find(name).text
  except AttributeError:
    return default

def saveVal(name,value):
  #Save a value in the config file, constructing a new element if it isn't there already.
  elem=xml.find(name)
  if elem==None:
    elem=ET.SubElement(xml.getroot(),name)
  elem.text=str(value)

def load():
  global campath,xml,FN,values
  campath='/var/lib/picam/'
  FN=campath+'config.xml'
  xml=ET.ElementTree()
  try:
    xml.parse(FN)
  except IOError:
    xml=ET.ElementTree(ET.XML('<config/>'))

  for k in values.keys():
    values[k][0]=values[k][2](getVal(k,values[k][0]))


def save():
  for k in values.keys():
    saveVal(k,values[k][3](values[k][0]))
  try:
    xml.write(FN)
  except IOError:
    print "<h2>Can not write config.xml. Permission problem? Changes lost!</h2>"
    return False
  return True

if __name__ == "__main__":
  #If config.py is run directly, return all the saved values as "name=value" pairs.
  #This is run from ftpsync.sh
  load()
  for k in values.keys():
    print k+'="'+values[k][3](values[k][0])+'"'

