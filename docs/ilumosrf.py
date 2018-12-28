#!/usr/bin/python
# ilumosrxrf.py
# try to capture iLumos rf codes
# capture into a buffer until long gap then back track to the previous message
#
# Author : Bob Tidey
# Date   : 26/12/2018
import time
import RPi.GPIO as GPIO
import array

CODE_LENGTH = 48
MIN_PULSE = 120
MAX_PULSE = 600
START_PULSE = 400
ONE_PULSE1 = 190
ONE_PULSE2 = 310
SKIP_BUFFERS = 4
SKIP_LENGTH = (CODE_LENGTH + 2) * SKIP_BUFFERS + 2

#analyse buffer after trigger
def analyseBuffer(index):
	code = 0
	for i in range(index, index + CODE_LENGTH - 2, 2):
		code = code * 2
		if(buffer[i] < 190 and buffer[(i + 1)] > 310):
			code = code + 1
	return code

# -----------------------
# Main Script
# -----------------------
STATE_START = 0
STATE_START1 = 1
STATE_BUFFER = 2
STATE_COMPLETE = 3
state = STATE_START
pulseCount = 0
skipCount = 0

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_RXDATA = 24

# Set pin for input
GPIO.setup(GPIO_RXDATA,GPIO.IN)  #
buffer = array.array('L',(0 for i in range(0, 2* CODE_LENGTH+2)))

# Wrap main content in a try block so we can
# catch the user pressing CTRL-C and run the
# GPIO cleanup function. This will also prevent
# the user seeing lots of unnecessary error
# messages.
try:
	oldrx = GPIO.input(GPIO_RXDATA)
	newrx = oldrx
	oldtime = time.time()
	newtime = oldtime
	while True:
		print "Waiting for capture"
		while state < STATE_COMPLETE:
			newrx = GPIO.input(GPIO_RXDATA)
			if (newrx != oldrx):
				newtime = time.time()
				diff = int((newtime - oldtime) * 1000000)
				if(diff < MIN_PULSE or diff > MAX_PULSE):
					state = STATE_START
				else:
					if (state == STATE_START):
						if(diff > START_PULSE and newrx == 0):
							state = STATE_START1
					elif(state == STATE_START1):
						if(diff > START_PULSE and newrx == 1):
							state = STATE_BUFFER
							pulseCount = 0
							skipCount = 0
						else:
							state = STATE_START
					elif(state== STATE_BUFFER):
						if(skipCount >= SKIP_LENGTH):
							buffer[pulseCount] = diff
							pulseCount +=1
							if(pulseCount >= CODE_LENGTH*2 + 2):
								state = STATE_COMPLETE
						else:
							skipCount += 1
							
				oldtime = newtime
				oldrx = newrx
		print "analysing data"
		code1 = analyseBuffer(0)
		code2 = analyseBuffer(CODE_LENGTH+2)
		if(code1 == code2):
			print format(code1,'06X')
			time.sleep(1)
		state = STATE_START

except KeyboardInterrupt:
	# User pressed CTRL-C
	print "Finished code capture"

GPIO.cleanup()
