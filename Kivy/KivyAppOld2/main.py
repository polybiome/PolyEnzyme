from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.clock import Clock
from kivy.graphics.vertex_instructions import (Rectangle,
											   Ellipse,
											   Line,
											   Triangle)
from kivy.graphics.context_instructions import Color
from kivy.properties import ListProperty,BooleanProperty,StringProperty,NumericProperty, ObjectProperty
import matplotlib.pyplot as plt
from kivy.uix.image import Image

#from kivy.graphics import *

from settingsjson import settings_json

import inspect
import random
import numpy as np

class MainCanvas(BoxLayout):
	def on_deletingNodes(self):
		print('nodes being deleted')

class OptionsCanvas(BoxLayout):
	pass
class OptionsButton(Button):
	pass

class NodeCanvas(FloatLayout):
	compounds = ListProperty([])
	reactions = ListProperty([])
	blocked = BooleanProperty(False)
	pressed = ListProperty([0, 0])
	temporalInput = StringProperty('')
	linkingReaction = BooleanProperty(False)
	deletingNodes = BooleanProperty(False)

	#WARNING: DO NOT UPDATE AUTOMATICALLY BASED ON SETTING'S SAVED VALUE: TO DO
	tmax = NumericProperty(2) 
	dt = NumericProperty(0.01)
	resolution = NumericProperty(0.01)

	def solveSystem(self):

		compounds = {}
		for compoundObj in self.compounds:
			compounds[compoundObj.name] = compoundObj.c

		print(compounds)

		def integrateODES(compounds,reactions,tmax,dt,resolution):
			y = {}
			for key in compounds.keys():
				y[key] = []
			for iterator in range(int(tmax/resolution)):
				for reaction in reactions:
					if reaction.rType == 'none':
						v0 = (reaction.vMax*compounds[reaction.S.name])/(reaction.km + compounds[reaction.S.name])
					elif reaction.rType == 'c':
						v0 = (reaction.vMax*compounds[reaction.S.name])/(reaction.km*(1+(compounds[reaction.I.name]/reaction.ki)) + compounds[reaction.S.name])  
					elif reaction.rType == 'u':
						v0 = (reaction.vMax*compounds[reaction.S.name])/(reaction.km + compounds[reaction.S.name]*(1+(compounds[reaction.I.name]/reaction.ki))) 
					elif reaction.rType == 'n':
						v0 = (reaction.vMax*compounds[reaction.S.name])/(reaction.km*(1+(compounds[reaction.I.name]/reaction.ki)) + compounds[reaction.S.name]*(1+(compounds[reaction.I.name]/reaction.ki)))
				
					compounds[reaction.S.name] += dt* -v0
					compounds[reaction.P.name] += dt* v0
				
				for compound in compounds:
					y[compound].append(compounds[compound])
						
			return y

		t = np.arange(0,self.tmax,self.resolution)

		sol = integrateODES(compounds,self.reactions,self.tmax,self.dt,self.resolution)

		for name, value in sorted(sol.items()):
			plt.plot(t, value, label=name)
		
		plt.legend(loc='best')
		plt.xlabel('t')
		plt.grid()
		#plt.show()
		plt.savefig('img/odeResult.png')
		plt.clf()

		#SHOW RESULT

		box = BoxLayout(orientation = 'vertical')
		odeResult = Image(source = 'img/odeResult.png')
		odeResult.reload()
		box.add_widget(odeResult)
		btn1 = Button(text='Done',size_hint= (1, .2))
		box.add_widget(btn1)
		myPopup = ResultPopup(content = box, auto_dismiss=True)
		btn1.bind(on_press = myPopup.dismiss)

		myPopup.open()

	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos) and self.blocked == False:
			for child in self.children:
				try:
					if child.isclicked(touch):
						return super(NodeCanvas, self).on_touch_down(touch)
				except AttributeError:
					pass
					#print('Error detected')
			self.pressed = touch.pos
			return True
		return super(NodeCanvas, self).on_touch_down(touch)

	def printCompounds(self):
		print('#####COMPOUNDS######')
		for compound in self.compounds:
			print(compound.name)
		print('######################')

	def printReactions(self):	
		print('#####REACTIONS######')
		for reaction in self.reactions:
			try:
				print('From '+reaction.S.name+' to '+reaction.P.name)
			except:
				print('From '+reaction.S.name+' to '+reaction.P)
		print('######################')

	#CREATES THE NODES#
	def on_pressed(self, instance, pos):
		self.compounds.append(GraphNode(
			center=pos,
			size_hint=(None,None)))

		self.add_widget(self.compounds[-1])

		self.printCompounds()
		#self.printReactions()

		def on_textName(instance, value):
			self.compounds[-1].name = value

		def on_textC(instance, value):
			try:
				convertedVal = float(value)
			except:
				convertedVal = 0
			self.compounds[-1].c = convertedVal

		box = BoxLayout()
		inputName = TextInput(text='Enter Name',multiline=False)
		inputC = TextInput(text='Enter Concentration', multiline=False, input_filter = 'float')

		inputName.bind(text=on_textName)
		inputC.bind(text=on_textC)
		
		box.add_widget(inputName)
		box.add_widget(inputC)

		btn1 = Button(text='Done')
		box.add_widget(btn1)
		myPopup = NodePopup(content = box, auto_dismiss=False)
		btn1.bind(on_press = myPopup.dismiss)

		myPopup.open()

	def removeNodeFromList(self,node):
		###REMOVE MY NODE OF LIST###
		self.compounds.remove(node)
		self.removeAssociatedNodeReactions(node)

	def removeAssociatedNodeReactions(self,node):
		###REMOVE ASSOCIATED REACTIONS###
		for reaction in self.reactions:
			if (reaction.S == node or reaction.P == node or reaction.I == node):
				reaction.boxText = ''
				reaction.myLine.points = []

		self.reactions[:] = [reaction for reaction in self.reactions if not (reaction.S == node or reaction.P == node or reaction.I == node)]

		self.printCompounds()
		self.printReactions()

	def removeAllNodes(self):
		print('REMOVING ALL NODES')
		for compound in self.compounds:
			self.removeAssociatedNodeReactions(compound)
			self.remove_widget(compound)
		self.compounds = []
		self.printCompounds()
		self.printReactions()		

class ResultPopup(Popup):
	def on_open(self):
		NodeCanvas.blocked = True
	def on_dismiss(self):
		NodeCanvas.blocked = False		

class NodePopup(Popup):

	def on_open(self):
		NodeCanvas.blocked = True
	def on_dismiss(self):
		NodeCanvas.blocked = False	

class ReactionPopup(Popup):

	def on_open(self):
		NodeCanvas.blocked = True
	def on_dismiss(self):
		NodeCanvas.blocked = False   

class GraphNode(Label):

	name = StringProperty('Default')
	c = NumericProperty(0)

	# def __init__(self, **kwargs):
	#	 super(GraphNode, self).__init__(**kwargs) 
	#	 self.setNumber()

	def on_touch_down(self, touch):
		self.col = (0.5,0,0.5,0.3)
		if self.collide_point(*touch.pos):
			touch.grab(self)
			###REMOVE NODE###

			if self.parent.deletingNodes:#EnzimeDynamicsApp.get_running_app().deletingNodes:
				print('DELETING NODES ON')
				self.parent.removeNodeFromList(self)
				self.parent.remove_widget(self)

			###CREATE REACTION###
			if touch.is_double_tap:
				print('--node clicked--')
				if not self.parent.linkingReaction:
					NodeCanvas.blocked = True
					self.parent.reactions.append(Reaction(S = self))
					self.parent.add_widget(self.parent.reactions[-1])
					#self.parent.printReactions()
					self.parent.linkingReaction = True
					with self.canvas:
						Color(0.5,0,0.5,0.3)
						Ellipse(size = self.size, pos = self.pos)
				else:
					NodeCanvas.blocked = False
					self.parent.reactions[-1].P = self
					fromNode = self.parent.reactions[-1].S
					textPos_x = (self.pos[0] + fromNode.pos[0])/2
					textPos_y = (self.pos[1] + fromNode.pos[1])/2
					self.parent.reactions[-1].boxPosition = [textPos_x,textPos_y]

					self.parent.printReactions()
					self.parent.printCompounds()

					self.parent.linkingReaction = False
					#print(self.parent.reactions[-1].S.canvas.children[-1])
					self.parent.reactions[-1].S.canvas.remove(self.parent.reactions[-1].S.canvas.children[-1])
					with self.canvas:
						Color(0.5,0,0.5,1)
						toNodeX = self.center[0]
						toNodeY = self.center[1] - self.height/2
						self.parent.reactions[-1].myLine = Line(points=
							self.returnLinePoints(fromNode.center[0],fromNode.center[1] - fromNode.height/2,
								self.center[0],self.center[1] - self.height/2), width=2)

					def on_inputKm(instance, value):
						try:
							convertedVal = float(value)
						except:
							convertedVal = 0
						self.parent.reactions[-1].km = convertedVal
						self.changeText()

					def on_inputVmax(instance, value):
						try:
							convertedVal = float(value)
						except:
							convertedVal = 0
						self.parent.reactions[-1].vMax = convertedVal
						self.changeText()

					box = BoxLayout()
					inputKm = TextInput(text='Enter KM',multiline=False, input_filter = 'float')
					inputVmax = TextInput(text='Enter Vmax ', multiline=False, input_filter = 'float')

					inputKm.bind(text=on_inputKm)
					inputVmax.bind(text=on_inputVmax)
					
					box.add_widget(inputKm)
					box.add_widget(inputVmax)

					btn1 = Button(text='Done')
					box.add_widget(btn1)
					myPopup = ReactionPopup(content = box, auto_dismiss=False)

					btn1.bind(on_press = myPopup.dismiss)
					
					myPopup.open()
					self.changeText()

	def changeText(self):
		self.parent.reactions[-1].boxText = 'km ' + str(self.parent.reactions[-1].km) + '\nVmax ' + str(self.parent.reactions[-1].vMax)

	def returnLinePoints(self, fromNodeX,fromNodeY,toNodeX,toNodeY):
		with self.canvas.after:
			h = 30
			w = h/4
			disX = toNodeX - fromNodeX
			disY = toNodeY - fromNodeY# - fromNode.height/2
			beta = np.arctan2(disY,disX)
			#beta = np.pi/2
			p = np.sqrt(h**2 + w**2)
			alphaU = beta - np.arcsin(w/p)
			xUd = p*np.cos(alphaU)
			yUd = p*np.sin(alphaU)

			xU = toNodeX - xUd
			yU = toNodeY - yUd

			gamma = np.pi/2 - beta
			wDis= 2*w*np.cos(gamma)
			hDis= 2*w*np.sin(gamma)

			xL = xU + wDis
			yL = yU - hDis

			return [fromNodeX,fromNodeY,toNodeX,toNodeY,xU,yU,toNodeX,toNodeY,xL,yL]

	def on_touch_move(self, touch):
		if touch.grab_current is self:
			self.center=[touch.x, touch.y]
			try:
				for reaction in self.parent.reactions:
					if reaction.S == self:
						reaction.myLine.points = (
							self.returnLinePoints(reaction.S.center[0],reaction.S.center[1] - reaction.S.height/2,
								reaction.P.center[0],reaction.P.center[1] - reaction.P.height/2))
						

						textPos_x = (reaction.S.pos[0] + reaction.P.pos[0])/2
						textPos_y = (reaction.S.pos[1] + reaction.P.pos[1])/2
						reaction.boxPosition = [textPos_x,textPos_y]
					elif reaction.P == self:
						reaction.myLine.points = (
							self.returnLinePoints(reaction.S.center[0],reaction.S.center[1] - reaction.S.height/2,
								reaction.P.center[0],reaction.P.center[1] - reaction.P.height/2))
						
						reaction.myLine.points = reaction.myLine.points
						textPos_x = (reaction.S.pos[0] + reaction.P.pos[0])/2
						textPos_y = (reaction.S.pos[1] + reaction.P.pos[1])/2
						reaction.boxPosition = [textPos_x,textPos_y]
					elif reaction.I == self:
						pass
			except AttributeError:
				print('WARNING: user grabed non-node object')


	def on_touch_up(self, touch):
		self.col = (.9,.9,.9,1)
		if touch.grab_current is self:
			touch.ungrab(self)

	def isclicked(self,touch):
		if self.collide_point(*touch.pos):
			return True
		return False

class Reaction(Label):
	boxPosition = ListProperty([0,0])
	boxText = StringProperty('')
	myLine = ObjectProperty(None)

	rType = StringProperty('none')
	km = NumericProperty(0.5)
	vMax = NumericProperty(1)
	Ki = NumericProperty()
	I = ObjectProperty('none')
	S = ObjectProperty('none')
	P = ObjectProperty('none')

class EnzimeDynamicsApp(App): 
	icon = 'img/ico.png'
	title = 'Enzyme Dynamics'

	def build(self):
		self.use_kivy_settings = False
		return MainCanvas()

	def build_config(self,config):
		config.setdefaults('ODEsettings',{
			'tmax': 2,
			'dt': 0.01,
			'resolution': 0.01
			})
		config.setdefaults('Other',{
			'optionsexample': 'option2',
			'stringexample': 'some_string',
			'pathexample': '/some/path'
			})
	def build_settings(self,settings):
		settings.add_json_panel('Settings', self.config, data=settings_json)

	def on_config_change(self, config, section, key, value):
		
		if section == 'ODEsettings':
			setattr(self.root.ids.myNodeCanvas,key,float(value))

		else:
			print(key,value)

if __name__ == "__main__":
	EnzimeDynamicsApp().run()