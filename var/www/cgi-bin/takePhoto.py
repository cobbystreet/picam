#!/usr/bin/python

import sys
import datetime

def takePhoto(config,now=datetime.datetime.today()):
  #Take a photo with the given config and save to file with the given name pattern
  #Preference is given to a webcam because opencv provides better error checking.
  CFN=config.campath+'current.jpg'
  FN=config.campath+'images/'+now.strftime(config.values['FNpattern'][0])
  import cv2
  cam = cv2.VideoCapture(0)
  #CV_CAP_PROP_FRAME_WIDTH
  cam.set(3,config.values['FrameWidth'][0])
  #CV_CAP_PROP_FRAME_HEIGHT
  cam.set(4,config.values['FrameHeight'][0])
  retval, image = cam.read()
  if retval:
    cam.release()
    cv2.imwrite(CFN,image)
  else:
    import picam
    image=picam.takePhotoWithDetails(config.values['FrameWidth'][0],config.values['FrameHeight'][0], 100)
    image.save(CFN)
  import shutil
  shutil.copyfile(CFN,FN)
  return FN


if __name__ == "__main__":
  #This is run if a user calls the script directly. It takes a picture with the saved settings
  #and returns it to the browser.
  import config
  config.load()
  #This is for testing only, so reduce resolution
  config.values['FrameWidth'][0]=640
  config.values['FrameHeight'][0]=480
  FN=takePhoto(config)
  if (FN!=None):
    sys.stdout.write("Content-type: image/jpeg\n\n")
    image=open(FN,'r')
    sys.stdout.write(image.read())
    image.close()

  #What follows was a rather roundabout way to delivering the result back to the web browser
  #without saving it to disk first.

  #import Image
  ##PIL expects RGB but the OpenCV image is BGR
  #pi = Image.fromstring("RGB", image.shape[:2][::-1], image[:,:,::-1].tostring())
  #import StringIO

  #output = StringIO.StringIO()
  #pi.save(output,format="JPEG")
  #contents = output.getvalue()
  #print output.getvalue()
  #output.close()

