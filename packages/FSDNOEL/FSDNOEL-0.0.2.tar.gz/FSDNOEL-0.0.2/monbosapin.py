#!/usr/bin/env python
# -*- coding:utf-8 -*


'''
	Mon beau Sapin de Noel
'''

#Pour travailler sur les sources
import sys
sys.path.insert(0,'../FGPIO')
sys.path.insert(0,'../FUTIL')

from FSDNOEL.sapin import *
import time
from FUTIL.my_logging import *
from FGPIO.hcsr501_io import *
from FGPIO.relay_io import *
from FGPIO.prise import *

my_logging(console_level = DEBUG, logfile_level = INFO, details = False)

pc = rpiduino_io()

monSapin = sapin( \
			#guirlande = relay_io(pc.bcm_pin(5)), \
			guirlande_RF = prise(rcSwitch_io(*pc.bcm_pins(20)), '00010', '00100'), \
			detecteur_ir = hcsr501_io(pc.bcm_pin(21)) \
			)

print "Ctrl-C pour stopper"			
try:
	while True:
		time.sleep(1)
except KeyboardInterrupt:
		monSapin.stop()

			

