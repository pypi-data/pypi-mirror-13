# -*-coding:Latin-1 -*

import Tkinter
import logging
from Fkanban import *

class ui_Fkanban(Tkinter.Tk, Fkanban):
	''' Interface graphique Application Fkanban
	'''
	def __init__(self, workshops = [], loops = [], parent=None, speed=1):
		'''Initialisation
			- fkanban	:	Fkanban object
			- parent	:	parent Tkinter object (default : None)
		'''
		Fkanban.__init__(self, workshops, loops, speed)
		Tkinter.Tk.__init__(self, parent)
		self.parent = parent
		self.initialise()
		
	def initialise(self):
		''' Initialise les widgets
		'''
		self.title('Fkanban')
		self.grid()
		column = 1
		for loop in self.loops:
			loop.ui_init(self, column, 2)
			column+=1
		
		Tkinter.Button(self, text=u'Next tour', command=self.on_bt_start).grid(column=0, row=0)
		Tkinter.Button(self, text=u'auto run', command=self.auto_run).grid(column=1, row=0)
		self.ui_time = Tkinter.Label(self, text=str(self.time))
		self.ui_time.grid(column = 2, row = 0)
		self.ui_update_kanbans()
		self.mainloop()
		
	def on_bt_start(self):
		''' on start button pressed
		'''
		self.run_actions()
		self.update()
		
	def ui_update_kanbans(self):
		logging.debug("Updating all ui_kanban")
		for loop in self.loops:
			for kb in loop.kanbans:
				kb.ui_update()
			# loop.place_kanbans()
		self.update()
		self.update_time()
	
	def update_time(self):
		''' Change the time on ui
		'''
		self.ui_time['text']=str(self.time)