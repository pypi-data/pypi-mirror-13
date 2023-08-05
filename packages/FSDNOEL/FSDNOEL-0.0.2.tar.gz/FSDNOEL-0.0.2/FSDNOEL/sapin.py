#!/usr/bin/env python
# -*- coding:utf-8 -*


'''
	Un Sapin de Noel à base de 
		- Sapin
		- Raspberry pi
		- guirlande + relais
		- detecteur de mouvement IR
		- ...
'''
#Pour travailler sur les sources
import sys
sys.path.insert(0,'../FGPIO')
sys.path.insert(0,'../FUTIL')

#from FGPIO.relay_io import *
#from FGPIO.ir_detect_io import *
from FUTIL.my_logging import *

class sapin(object):
	'''Un Sapin de Noel avec une Raspberry dedans
	'''
	def __init__(self, guirlande = None, clignotte_on = 5, clignotte_off = 2, guirlande_RF = None, detecteur_ir = None):
		'''Initialisation
			- guirlande	:	FGPIO.relay_io
			- clignotte_on	:	Durée du clignottement "on" de la guirlande
			- clignotte_off	:	Durée du clignottement "off" de la guirlande
			- guirelande_RF :	Prise RF sur laquelle est branchee un guirlande qui clignote toutes seule
			- detecteur_ir	:	FGPIO.ir_detect_io
		'''
		self.guirlande = guirlande
		self.detecteur_ir = detecteur_ir
		self.clignotte_on = clignotte_on
		self.clignotte_off = clignotte_off
		self.guirlande_RF = guirlande_RF
		if self.detecteur_ir:
			self.detecteur_ir.add_thread(self.on_detecteur_ir_change)
		else:
			logging.debug("La guirlande va clignotter pour toujours")
			self.clignotte()
			
		
	def clignotte(self, marche = True):
		'''Fais clignotter indéfiniment la guirlande
			- marche	:	Si True		: débute le clignottement
							Si False	: stop le clignottement
		'''
		if self.guirlande:
			if marche :
				self.guirlande.blink(self.clignotte_on,self.clignotte_off)
			else:
				self.guirlande.stop()
	
	def clignotte_guirelande_RF(self, marche = True):
		'''Allume une guirlande branche sur une prise RF
		'''
		if self.guirlande_RF:
			self.guirlande_RF.set(marche)
		
	def on_detecteur_ir_change(self):
		'''Deamon quand le detecteur IR change d'état
		'''
		if self.detecteur_ir.th_readed():
			logging.debug("Detection de mouvement : la guirlande clignotte")
			self.clignotte()
			self.clignotte_guirelande_RF()
		else:
			logging.debug("Plus de mouvement : la guirlande stoppe")
			self.clignotte(False)
			self.clignotte_guirelande_RF(False)
	
	def stop(self):
		'''Stop tous les threads
		'''
		if self.guirlande:
			self.guirlande.stop()
		if self.detecteur_ir:
			self.detecteur_ir.stop()