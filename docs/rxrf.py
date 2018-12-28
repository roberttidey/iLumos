#!/usr/bin/python
# rxrf.py
# log transitions from an rf receiver module
# captures MAX_FILES of MAX_BUFFER transitions
# Each filename is incremented by 1.
# contains a level followed by microsec delay from last change
#
# Author : Bob Tidey
# Date   : 12/04/2013
import time
import RPi.GPIO as GPIO
import array

# -----------------------
# Main Script
# -----------------------
MAX_BUFFER = 40000 # twice number of samples per file
MAX_FILES = 2
ROOT_FILENAME = "rxdata"
#Wait till at least trigger of silence (seconds) to start capture
# Can be used if there is a known quiet period before a message
#Set to 0 to capture straight away
#For Lightwave capture put in 0.009 as each message is preceded by this
TRIGGER = 0.009

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_RXDATA = 24

print "Logging RX transitions"

# Set pin for input
GPIO.setup(GPIO_RXDATA,GPIO.IN)  #
buffer = array.array('L',(0 for i in range(0,MAX_BUFFER)))
findex = 0

# Wrap main content in a try block so we can
# catch the user pressing CTRL-C and run the
# GPIO cleanup function. This will also prevent
# the user seeing lots of unnecessary error
# messages.
try:
   while findex < MAX_FILES:
      oldrx = GPIO.input(GPIO_RXDATA)
      newrx = oldrx
      oldtime = time.time()
      newtime = oldtime
      triggered = 0
      count = 0
      while triggered == 0:
         newrx = GPIO.input(GPIO_RXDATA)
         if (newrx != oldrx):
            newtime = time.time()
            if ((newtime - oldtime) >  TRIGGER):
               triggered = 1
               buffer[count] = newrx
               count += 1
               buffer[count] = long((newtime - oldtime) * 1000000)
               count += 1
            oldtime = newtime
            oldrx = newrx

      while count < MAX_BUFFER - 2:
         newrx = GPIO.input(GPIO_RXDATA)
         if (newrx != oldrx):
            newtime = time.time()
            buffer[count] = newrx
            count += 1
            buffer[count] = long((newtime - oldtime) * 1000000)
            count += 1
            oldtime = newtime
            oldrx = newrx
      findex = findex + 1
      with open(ROOT_FILENAME + str(findex), "wb") as f:
         f.write(time.strftime("%d/%m/%Y %H:%M:%S"))
         f.write('\n')
         for i in range(0, MAX_BUFFER-1, 2) :
            f.write(repr(buffer[i]).rjust(4))
            f.write(repr(buffer[i+1]).rjust(8))
            f.write('\n')
		 f.close()
      print "Logged file " + str(findex)
except KeyboardInterrupt:
   findex = 0
# User pressed CTRL-C
print "Finished Logging RX transitions"

GPIO.cleanup()
