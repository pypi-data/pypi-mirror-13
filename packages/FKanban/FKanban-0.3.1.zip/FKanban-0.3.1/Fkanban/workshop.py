# -*-coding:Latin-1 -*
from ui_object import *

class workshop(ui_object):
	''' a workshop with kanbans
	'''
	def __init__(self, name):
		'''Initialisation
			- name
		'''
		self.name = name
		self.kanban_to_do = []
	
	def __str__(self):
		return self.name