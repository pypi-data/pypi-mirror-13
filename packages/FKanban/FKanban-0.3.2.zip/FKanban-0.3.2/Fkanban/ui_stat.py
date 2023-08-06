# -*-coding:Latin-1 -*
import Tkinter
import logging
from kloop import *

class ui_stat(Tkinter.Tk):
	'''Windows for stat.
	'''
	def __init__(self, loop):
		'''Initialisation
			- loop	:	kanban loop
		'''
		Tkinter.Tk.__init__(self, None)
		self.loop=loop
		self.title('Statistiques for %s'%(loop.name))
		#self.grid()
		self.bt_refresh = Tkinter.Button(self, text=u'Refresh', command=self.refresh)
		self.bt_refresh.pack()
		self.list = Tkinter.Listbox(self, width = 50)
		self.list.pack(fill=Tkinter.BOTH, expand=1)
		self.refresh()
		#self.mainloop()
		
	
	def refresh(self):
		'''Refresh the window
		'''
		self.list.delete(0,Tkinter.END)
		for stat in self.loop.time_stock_in:
			self.list.insert(Tkinter.END, "time = %s : production = %s"%stat)