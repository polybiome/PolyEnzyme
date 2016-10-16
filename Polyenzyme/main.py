from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.spinner import Spinner
from kivy.uix.settings import Settings,InterfaceWithNoMenu
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics.instructions import InstructionGroup
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import (Rectangle,
											   Ellipse,
											   Line,
											   Triangle)
from kivy.graphics.context_instructions import Color
from kivy.properties import ListProperty,BooleanProperty,StringProperty,NumericProperty, ObjectProperty, OptionProperty, BoundedNumericProperty
from kivy.config import Config
from kivy.uix.image import Image
from settingsjson import settings_json
from kivy.input.motionevent import MotionEvent
#from kivy.lang import Builder

import matplotlib.pyplot as plt
import tkinter
import tkinter.filedialog
import inspect
import random
import json
import copy
import os
import numpy as np
import requests

from functools import partial

#Constants
#Window.fullscreen = 1#'auto'#False#'auto'
#Window.window_state = 'maximized'
Config.set('graphics', 'window_state', 'maximized')
Config.set('kivy', 'exit_on_escape', '0')
Config.set("input", "mouse", "mouse,disable_multitouch")

defaultFillColor = [0.9,0.9,0.9,0.5]
defaultContextColor = [198/255,40/255,40/255,0.8]
sourcesContextColor = [0/255, 137/255, 123/255,0.8]
productsContextColor = [46/225, 125/255, 50/255,0.8]
defaultNodeSize = [100,100]
defaultArrowSize1Final = 15
defaultArrowSize2Final = 30
defaultWidth = 2
defaultArrowSize = 20
defaultInhibitionH = 0.1
defaultInhibitionW = 5
defaultGridDivision = 40
zoomRes = 5
specialEffectDelay = 20

class MainCanvas(Screen):
	contextText = StringProperty('Create\nReaction')
	contextColor = ListProperty(defaultContextColor)#[41/255, 182/255, 246/255, 1])
	myReactionHelper = ObjectProperty()

	def on_enter(self,*args):
		myInitialInstructions = InitialInstructions()
		self.ids.myNodeCanvas.add_widget(myInitialInstructions)

		self.ids.myNodeCanvas.addGrid()

	def on_deletingNodes(self):
		print('nodes being deleted')

class NodeCanvas(FloatLayout):
	compounds = ListProperty([])
	reactions = ListProperty([])
	blocked = BooleanProperty(False)
	pressed = ListProperty([0, 0])
	deletingNodes = BooleanProperty(False)
	settingS = BooleanProperty(False)
	settingP = BooleanProperty(False)
	clickedS = ListProperty()
	clickedP = ListProperty()
	totalC = NumericProperty(0)
	movingCanvas = StringProperty('0')
	#dFromClick = ListProperty([0,0])

	timeClock = NumericProperty(0)
	timeClock2 = NumericProperty(0)
	movingNode = BooleanProperty(False)
	firstTouch = BooleanProperty(True)
	secondInfo = BooleanProperty(True) 
	gridAdded = BooleanProperty(False)
	grid = ObjectProperty('Default')
	gridColor = ObjectProperty('Default')
	once = BooleanProperty(True)

	simulationSpeed = BoundedNumericProperty(0, min=0, max=100)
	scrollPos = NumericProperty(0)


	tmax = NumericProperty(2) 
	dt = NumericProperty(0.01)

	def __init__(self, **kwargs):
		super(NodeCanvas, self).__init__(**kwargs)
		Clock.schedule_interval(self.animVarious, 1/90)

		Window.bind(on_resize= partial(self.updateWindow, self), on_enter = partial(self.updateWindow, self),on_draw= partial(self.updateWindow, self))
		Window.bind(on_motion=self.canvasMove)
		self.gridTexture = Image(source = 'img/cell.png').texture
		self.gridTexture.wrap = 'repeat'

	def canvasMove(self, etype, motionevent, touch):

		if 'button' in touch.profile:
			if touch.button == 'scrolldown' and self.scrollPos < 5 and self.once:
				self.once = False
				self.scrollPos +=1
				Clock.schedule_once(self.unblockOnce, 0.1)
				for compound in self.compounds:
					centerB = compound.center
					for k in range(2):
						compound.size[k] += 4*zoomRes
					compound.center[0] -= 0.2*(touch.spos[0]*Window.width - compound.center[0])
					compound.center[1] -= 0.2*(touch.spos[1]*Window.height - compound.center[1])
					compound.updateReactions()

			if touch.button == 'scrollup' and self.scrollPos > -4 and self.once:
				self.once = False
				self.scrollPos -=1
				Clock.schedule_once(self.unblockOnce, 0.1)
				for compound in self.compounds:
					centerB = compound.center
					for k in range(2):
						compound.size[k] -= 4*zoomRes
					compound.center[0] += 0.2*(touch.spos[0]*Window.width - compound.center[0])
					compound.center[1] += 0.2*(touch.spos[1]*Window.height - compound.center[1])
					compound.updateReactions()

	def unblockOnce(self,*args):
		self.once = True

	def on_simulationSpeed(self,*args):
		Clock.unschedule(self.simulateSystem)
		if self.simulationSpeed > 0.01:
			if self.simulationSpeed > 99.98:
				Clock.schedule_interval(self.simulateSystem, 0.00000000000000000000000001) #...
			else:
				Clock.schedule_interval(self.simulateSystem, 1/self.simulationSpeed)

	def updateWindow(self,*args):
		#print('updating window')
		if self.gridAdded:

			#gridDivision = defaultGridDivision+5*(1-defaultNodeSize[0]/self.compounds[0].size[0]) if self.compounds else defaultGridDivision
			gridDivision = defaultGridDivision*(self.compounds[0].size[0]/defaultNodeSize[0]) if self.compounds else defaultGridDivision

			self.canvas.before.remove(self.gridColor)
			self.canvas.before.remove(self.grid)
			self.gridTexture.uvsize = (int(self.width / gridDivision) ,int(self.height / gridDivision)) #20
			self.grid = Rectangle(size = self.size, texture = self.gridTexture, pos = self.pos)
			self.canvas.before.add(self.gridColor)
			self.canvas.before.add(self.grid)
		
	def addGrid(self):
		
		self.gridTexture.uvsize = (int(self.width / defaultGridDivision) ,int(self.height / defaultGridDivision)) #20
		self.grid = Rectangle(size = self.size, texture = self.gridTexture, pos = self.pos)
		self.gridColor = Color(244/255,244/255,244/255,0.2)
		self.canvas.before.add(self.gridColor)
		self.canvas.before.add(self.grid)
		self.gridAdded = True

	def saveData(self):
		
		data = {'compounds': [], 'reactions': [] }

		compoundData = {'pos':[],'size':[],'name':[],'c':[],'special':[],'fillColor':[],'totalC':[], 'myId':[]}
		reactionData = {'myId':[],'boxPosition':[],'boxText':[],'linkColor':[],'enzyme':[],'km':[],'vMax':[],'iBoxes':[],'I_ids':[],'S_ids':[],'P_ids':[]}
		iBoxData = {'I_ids':[],'ki':[],'rType':[],'iBoxText':[],'reaction_ids':[]}

		for compound in self.compounds:
			for key in compoundData:
				compoundData[key] = getattr(compound, key)
			data['compounds'].append(copy.copy(compoundData))

		for reaction in self.reactions:
			for key in reactionData:
				if key == 'iBoxes':
					for I in reaction.I: #Since the ibox is solely specified by its inhibitor
						for iBox in reaction.iBoxes:			
							if I == iBox.I:
								for key in iBoxData:
									if key == 'reaction_ids':
										iBoxData['reaction_ids'] = copy.copy(reaction.myId)
									elif key == 'I_ids':
										iBoxData['I_ids'] = I.myId
									else:
										iBoxData[key] = getattr(iBox, key)
								reactionData['iBoxes'].append(copy.copy(iBoxData))

				elif key == 'I_ids':
					reactionData['I_ids'].clear()
					for I in reaction.I:
						reactionData['I_ids'].append(I.myId)

				elif key == 'S_ids':
					reactionData['S_ids'].clear()
					for S in reaction.S:
						print(S.myId)
						print('#######')
						reactionData['S_ids'].append(S.myId)

				elif key == 'P_ids':
					reactionData['P_ids'].clear()
					for P in reaction.P:
						reactionData['P_ids'].append(P.myId)
				else:
					reactionData[key] = getattr(reaction, key)

			data['reactions'].append(copy.deepcopy(reactionData))

		print(data['reactions'])

		box = BoxLayout()

		text = ['_']

		def on_nameText(text, instance, value):

			text.append(value) #To pass by reference (4 sure there is a better way)

		def on_dissmissMyPoup(*args):

			if text[-1] == '':
				text[-1] = 'Default'

			with open('saved/' + text[-1] + '.json', 'w') as outfile:
				json.dump(data, outfile)

			myPopup.dismiss()

		inputName = TextInput(hint_text='Name',multiline=False)
		inputName.bind(text=partial(on_nameText,text))
		box.add_widget(inputName)

		btn1 = Button(text='Save')
		box.add_widget(btn1)
		myPopup = SaveDataPopup(content = box, auto_dismiss=False)
		btn1.bind(on_press = on_dissmissMyPoup)

		myPopup.open()		

	def openData(self):

		box = BoxLayout()

		database_url = 'https://rawgit.com/polybiome/database/master/database.txt'
		optionsCloud = requests.get(database_url)
		optionsCloud = optionsCloud.content
		optionsCloud = optionsCloud.decode().split(',')

		optionsLocal = os.listdir("saved/")

		def on_selectCloud(instance, value):
			url = 'https://rawgit.com/polybiome/database/master/' + str(value)
			r = requests.get(url.rstrip())
			data = json.loads(r.text)
			self.loadData(data)
			myPopup.dismiss()

		def on_selectLocal(instance, value):
			with open('saved/' + value, 'r') as fp:
				data = json.load(fp)
				self.loadData(data)
				myPopup.dismiss()

		spinnerCloud = Spinner(text='Select predefined:',values=optionsCloud, background_color = (255,255,255,1), font_size = 12, color = (0,0,0,1))

		spinnerLocal = Spinner(text='Select custom:',values=optionsLocal, background_color = (255,255,255,1), font_size = 12, color = (0,0,0,1))

		spinnerCloud.bind(text=on_selectCloud)
		spinnerLocal.bind(text=on_selectLocal)

		box.add_widget(spinnerCloud)
		box.add_widget(spinnerLocal)

		btn1 = Button(text='Cancel')
		box.add_widget(btn1)
		myPopup = OpenDataPopup(content = box, auto_dismiss=False)
		btn1.bind(on_press = myPopup.dismiss)

		myPopup.open()

	def loadData(self,data):

		for compound in data['compounds']:
			self.compounds.append(GraphNode(size_hint=(None,None)))
			for key in compound:
				setattr(self.compounds[-1], key, compound[key])
			self.add_widget(self.compounds[-1])
			self.compounds[-1].size = self.compounds[0].size if self.compounds else defaultNodeSize

			if (self.compounds[-1].pos[0]) < self.pos[0]:
				self.compounds[-1].pos[0] = self.pos[0]

		for reaction in data['reactions']:
			self.reactions.append(Reaction())
			self.add_widget(self.reactions[-1])
			for key in reaction:

				if key == 'I_ids':
					for I_id in reaction['I_ids']:
						for compound in self.compounds:
							if compound.myId == I_id:
								self.reactions[-1].I.append(compound)	

				if key == 'S_ids':
					for S_id in reaction['S_ids']:
						for compound in self.compounds:
							if compound.myId == S_id:
								self.reactions[-1].S.append(compound)

				elif key == 'P_ids':
					for P_id in reaction['P_ids']:
						for compound in self.compounds:
							if compound.myId == P_id:
								self.reactions[-1].P.append(compound)

				elif not key == 'iBoxes':
					setattr(self.reactions[-1], key, reaction[key])

			for iBox in reaction['iBoxes']:
				for myReaction in self.reactions:
					if myReaction.myId == iBox['reaction_ids']:
						myReaction.iBoxes.append(InhibitionPropierties(reaction = myReaction))
						self.add_widget(self.reactions[-1].iBoxes[-1])

				for compound in self.compounds:
					if compound.myId == iBox['I_ids']:
						self.reactions[-1].iBoxes[-1].I = compound

				for key in iBox:
					if not key == 'reaction_ids' and not key == 'I_ids':
						setattr(self.reactions[-1].iBoxes[-1], key, iBox[key])

				self.reactions[-1].createInhibitionLines(self.reactions[-1].iBoxes[-1].I)

			
			self.createReactionLines(self.reactions[-1].S,self.reactions[-1].P)

	def on_clickedS(self,*args):

		for compound in self.compounds:
			if compound in self.clickedS:
				compound.contextColor = self.parent.parent.contextColor
			elif compound not in self.clickedP:
				compound.contextColor = [0,0,0,1]

	def on_clickedP(self,*args):

		for compound in self.compounds:
			if compound in self.clickedP:
				compound.contextColor = self.parent.parent.contextColor
			elif compound not in self.clickedS:
				compound.contextColor = [0,0,0,1]

	def setDeletingNodes(self):
		self.deletingNodes = not self.deletingNodes
		for compound in self.compounds:
			compound.deletingNodes = not compound.deletingNodes

	def onCchange(self, *args):
		self.totalC = 0
		for compound in self.compounds:
			if not compound.special == 'sourceSink':
				self.totalC += compound.c
			else:
				compound.c = 0

		for compound in self.compounds:
			compound.totalC = self.totalC #Is there a better way?

	def simulateSystem(self, *args):
		if not self.settingP and not self.settingS and not self.deletingNodes and not self.blocked:
			self.reactionCycle(self.dt)

	def reactionCycle(self, dt):
		tempS = []
		tempP = []

		def MichaelisMentel(x,reaction):
			return (reaction.vMax*x)/(reaction.km + x)
		def MichelisMentelInhibition(x,reaction,competitiveIhibition,unCompetitiveIhibition):
			return (reaction.vMax*x)/(reaction.km*(1 + competitiveIhibition) + x*(1 + unCompetitiveIhibition))

		for k, reaction in enumerate(self.reactions):
			tempS.append([])
			tempP.append([])
			if not reaction.iBoxes:#all(x == 'none' for x in [ibox.rType for ibox in reaction.iBoxes]):
				try:
					sMult = 1
					hasSource = False
					for S in reaction.S:
						if S.special == 'sourceSink':
							hasSource = True
						else:
							sMult *= S.c
					if sMult == 0:
						v0 = 0
					elif hasSource:
						v0 = reaction.vMax
					else:
						v0Temp = MichaelisMentel(sMult,reaction)
						v0 = MichaelisMentel(sMult + v0Temp*dt/2,reaction)

					for S in reaction.S:
						if not S.special == 'sourceSink':
							if S.c >= dt*v0:
								#S.c += dt*-v0
								tempS[k].append(dt*-v0)
							else:
								S.c = 0 #Hard zero to allow the sMult==0 above
								tempS[k].append(0)

					for P in reaction.P:
						if not P.special == 'sourceSink':
							#P.c += dt* v0	
							tempP[k].append(dt* v0)

				except ZeroDivisionError as e:
					print('WARNING: ' + str(e))
			else:
				competitiveIhibition = 0
				unCompetitiveIhibition = 0
				for ibox in reaction.iBoxes: #Assumes that inhibitions add!
					if ibox.rType == 'c' or ibox.rType == 'nc':
						competitiveIhibition += ibox.I.c/ibox.ki
					if ibox.rType == 'uc' or ibox.rType == 'nc':
						unCompetitiveIhibition += ibox.I.c/ibox.ki
				try:
					sMult = 1
					hasSource = False
					for S in reaction.S:
						if S.special == 'sourceSink':
							hasSource = True
						else:	
							sMult *= S.c

					if sMult == 0:
						v0 = 0
					elif hasSource:
						v0 = reaction.vMax/(1 + unCompetitiveIhibition)
					else:
						v0Temp = MichelisMentelInhibition(sMult,reaction,competitiveIhibition,unCompetitiveIhibition)
						v0 = MichelisMentelInhibition(sMult + v0Temp*dt/2,reaction,competitiveIhibition,unCompetitiveIhibition)
						#v0 = (reaction.vMax*sMult)/(reaction.km*(1 + competitiveIhibition) + sMult*(1 + unCompetitiveIhibition))

					for S in reaction.S:
						if not S.special == 'sourceSink':
							if S.c >= dt*v0:
								tempS[k].append(dt*-v0)
							else:
								S.c = 0 #Hard zero to allow the sMult==0 above
								tempS[k].append(0)

					for P in reaction.P:
						if not P.special == 'sourceSink':
							tempP[k].append(dt* v0)

				except ZeroDivisionError as e:
					print('WARNING: ' + str(e))

		for k, reaction in enumerate(self.reactions):
			i = 0
			for S in reaction.S:
				if not S.special == 'sourceSink':
					S.c += tempS[k][i]
					i += 1
			i = 0
			for P in reaction.P:
				if not P.special == 'sourceSink':
					P.c += tempP[k][i]
					i += 1


	def solveSystem(self):

		self.blocked = True

		compounds = {}
		for compoundObj in self.compounds:
			compounds[compoundObj] = [compoundObj.c]

		print(compounds)

		def integrateODES(compounds,tmax,dt):

			for iterator in range(int(tmax/dt)):

				self.reactionCycle(dt)
				
				for compound in self.compounds:
					compounds[compound].append(compound.c)

			return compounds

		t = np.arange(0,self.tmax,self.dt)

		sol = integrateODES(compounds,self.tmax,self.dt)

		for obj, value in sol.items():
			if not obj.special == 'sourceSink':
				#fillColor = obj.fillColor[:-1]
				#plt.plot(t, value[:-1], label=obj.name,color = fillColor, linewidth=3)
				plt.plot(t, value[:-1], label=obj.name, linewidth=3)
		
		plt.legend(loc='best')
		plt.xlabel('t[s]')
		plt.ylabel('Concentration[mM]')
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

		self.blocked = False

		myPopup.open()

	def animVarious(self, *args):

		self.timeClock += 0.25
		if self.timeClock > 90:
			self.timeClock = 0


		if not self.movingNode:

			for reaction in self.reactions:
				linePos = -1
				centroidX = np.average([element.center[0] for element in (reaction.S + reaction.P)])
				centroidY = np.average([element.center[1] for element in (reaction.S + reaction.P)])
				centroidPX = np.average([element.center[0] for element in reaction.P])
				centroidPY = np.average([element.center[1] for element in reaction.P])

				for P in reaction.P:

					if len(reaction.P) == 1:
						arrowPos = 0.1
						if self.timeClock > 80:
							arrowPos1 = arrowPos + 0.5
							arrowSize1 = 0
						else:
							arrowPos1 =  arrowPos + 0.5*(np.sin(1/80*self.timeClock*(np.pi/2)))
							arrowSize1 = defaultArrowSize1Final*(P.size[0]/defaultNodeSize[0])*(1+np.sin(2*self.timeClock*np.pi/160))

						if self.timeClock < 20:
							arrowPos2 = arrowPos
							arrowSize2 = 0
						else:
							arrowPos2 =  arrowPos + 0.5*(np.sin(1/80*self.timeClock*(np.pi/2) - (20*np.pi/180)))

							arrowSize2 = defaultArrowSize2Final*(P.size[0]/defaultNodeSize[0])*np.sin(2*self.timeClock*np.pi/180 - (20*np.pi/180))
					else:
						arrowPos = np.sqrt((P.center[0] - centroidX)**2 + (P.center[1] - centroidY)**2)
						arrowPos = arrowPos/(arrowPos + 40)
						if self.timeClock > 80:
							arrowPos1 = 0.9
							arrowSize1 = 0
						else:
							arrowPos1 =  0.9*(np.sin(1/80*self.timeClock*(np.pi/2)))
							arrowSize1 = defaultArrowSize1Final*(P.size[0]/defaultNodeSize[0])*(1+np.sin(2*self.timeClock*np.pi/160))

						if self.timeClock < 20:
							arrowPos2 = arrowPos
							arrowSize2 = 0
						else:
							arrowPos2 = 0.9*(np.sin(1/80*self.timeClock*(np.pi/2) - (20*np.pi/180)))

							arrowSize2 = defaultArrowSize2Final*(P.size[0]/defaultNodeSize[0])*np.sin(2*self.timeClock*np.pi/180 - (20*np.pi/180))

	

					fromPointX,fromPointY,toPointX,toPointY = self.computeBezier([centroidX,centroidY],[centroidPX,centroidPY],P.center,arrowPos1)
					myPoints = self.returnPoints(fromPointX,fromPointY,toPointX,toPointY, arrowSize1, arrowSize1/4)
					reaction.myLines.children[linePos].points=myPoints

					linePos -=2

					fromPointX,fromPointY,toPointX,toPointY = self.computeBezier([centroidX,centroidY],[centroidPX,centroidPY],P.center,arrowPos2 - 0.1)
					myPoints2 = self.returnPoints(fromPointX,fromPointY,toPointX,toPointY,arrowSize2, arrowSize2/4)
					reaction.myLines.children[linePos].points=myPoints2

					linePos -=4

			# for compound in self.compounds:
			# 	if compound.special == 'sourceSink':
			# 		for k in range(5):
			# 			if self.timeClock < k*specialEffectDelay:
			# 				compound.specialEffectSize[k] = [0,0]
			# 			else:
			# 				compound.specialEffectSize[k] = [compound.size[0] * ((self.timeClock-k*specialEffectDelay)/(90-k*specialEffectDelay)), compound.size[1] * ((self.timeClock-k*specialEffectDelay)/(90-k*specialEffectDelay))]

			self.timeClock2 += 0.01
			if self.timeClock2 > 90:
				self.timeClock2 = 0

			for compound in self.compounds:
					if compound.special == 'sourceSink':
						for k in range(5):
							compound.specialEffectSize[k] = [(compound.size[0] * (1+np.sin(self.timeClock2 - k*specialEffectDelay)))/2,(compound.size[1] * (1+np.sin(self.timeClock2 - k*specialEffectDelay)))/2]#-k*specialEffectDelay)
					
	def buttonBehaviour(self):
		if not self.settingS and not self.settingP and not self.deletingNodes and len(self.compounds) > 1:
			self.blocked = True
			self.settingS = True
			self.clickedS.clear()
			self.clickedP.clear()

		elif self.settingS:
			self.settingS = False
			self.settingP = True

		elif self.settingP:
			self.settingS = False
			self.settingP = False			

		if self.settingS:
			self.parent.parent.contextText = 'Done'
			self.parent.parent.contextColor = sourcesContextColor
			self.parent.parent.myReactionHelper = ReactionHelper(contextColor = self.parent.parent.contextColor)
			self.parent.parent.myReactionHelper.ids.MyHelperLabel.text = 'Click the nodes to select all the substrates for your reaction. Press DONE to start selecting products.'
			self.parent.parent.add_widget(self.parent.parent.myReactionHelper)

		elif self.settingP:
			self.parent.parent.contextText = 'Done'
			self.parent.parent.contextColor = productsContextColor
			self.parent.parent.myReactionHelper.contextColor = self.parent.parent.contextColor
			self.parent.parent.myReactionHelper.ids.MyHelperLabel.text = 'Click the nodes to select all the products for your reaction, [b]or click an existing reaction to inhibit it[/b].'

		elif not self.deletingNodes and len(self.compounds) > 1:
			self.createReaction()
			self.parent.parent.contextText = 'Create\nReaction'
			self.parent.parent.contextColor = defaultContextColor
			for compound in self.compounds:
				compound.contextColor = [0,0,0,1]
			self.parent.parent.remove_widget(self.parent.parent.myReactionHelper)
			self.blocked = False

	def computeBezier(self,P0,P1,P2,arrowPos):
		t = arrowPos - 0.1
		fromPointX = (1-t)**2*P0[0] + 2*(1-t)*t*P1[0] + t**2*P2[0]
		fromPointY = (1-t)**2*P0[1] + 2*(1-t)*t*P1[1] + t**2*P2[1]
		t = arrowPos
		toPointX = (1-t)**2*P0[0] + 2*(1-t)*t*P1[0] + t**2*P2[0]
		toPointY = (1-t)**2*P0[1] + 2*(1-t)*t*P1[1] + t**2*P2[1]
		return(fromPointX,fromPointY,toPointX,toPointY)

	def createReaction(self):

		# for element in self.clickedS + self.clickedP:
		# 	element.canvas.remove(element.canvas.children[-1]) #Ellipsis(deprecated)

		if self.clickedS and self.clickedP:
			self.reactions.append(Reaction(S = self.clickedS,P = self.clickedP))
			self.add_widget(self.reactions[-1])
			self.createReactionLines(self.clickedS,self.clickedP)

			self.setReactionData(self.reactions[-1])

			for element in (self.clickedS + self.clickedP):
				element.changeFillColor()

		self.onCchange()
		self.clickedS.clear()
		self.clickedP.clear()
		#self.printCompounds()
		self.printReactions()

	def createReactionLines(self,clickedS,clickedP):
			centroidX = np.average([element.center[0] for element in (clickedS + clickedP)])
			centroidY = np.average([element.center[1] for element in (clickedS + clickedP)])
			centroidSX = np.average([element.center[0] for element in (clickedS)])
			centroidSY = np.average([element.center[1] for element in (clickedS)])
			centroidPX = np.average([element.center[0] for element in (clickedP)])
			centroidPY = np.average([element.center[1] for element in (clickedP)])

			self.reactions[-1].boxPosition = (int(centroidX),int(centroidY))

			#Ensures no two boxes are superposed
			for reaction in self.reactions[:-1]:
				if np.sqrt((self.reactions[-1].boxPosition[0] - reaction.boxPosition[0])**2 + (self.reactions[-1].boxPosition[1] - reaction.boxPosition[1])**2) < 0.1:
					
					beta = np.arctan2(centroidSY-centroidPY,centroidSX-centroidPX)

					reaction.boxPosition[0] -= int(np.sin(beta) * 50)
					reaction.boxPosition[1] -= int(np.cos(beta) * 50)
					
					self.reactions[-1].boxPosition[0] += int(np.sin(beta) * 50)
					self.reactions[-1].boxPosition[1] += int(np.cos(beta) * 50)
			##

			for S in clickedS:
				self.reactions[-1].myLines.add(Line(bezier=(S.center[0],S.center[1],centroidSX,centroidSY,centroidX,centroidY),width = defaultWidth*(S.size[0]/defaultNodeSize[0])))

			for P in clickedP:
				self.reactions[-1].myLines.add(Line(bezier=(centroidX,centroidY,centroidPX,centroidPY,P.center[0],P.center[1]), width = defaultWidth*(P.size[0]/defaultNodeSize[0])))
				
				arrowPos = np.sqrt((P.center[0] - centroidX)**2 + (P.center[1] - centroidY)**2)
				arrowPos = arrowPos/(arrowPos + 50)
				if len(clickedP) == 1:
					arrowPos = 0.4
				fromPointX,fromPointY,toPointX,toPointY = self.computeBezier([centroidX,centroidY],[centroidPX,centroidPY],P.center,arrowPos)
				myPoints = self.returnPoints(fromPointX,fromPointY,toPointX,toPointY,0,0)
				self.reactions[-1].myLines.add(Triangle(points=(myPoints)))
				

				arrowPos -= 0.1
				fromPointX,fromPointY,toPointX,toPointY = self.computeBezier([centroidX,centroidY],[centroidPX,centroidPY],P.center,arrowPos)
				myPoints = self.returnPoints(fromPointX,fromPointY,toPointX,toPointY,0,0)
				self.reactions[-1].myLines.add(Triangle(points=(myPoints)))
				
			self.canvas.before.add(Color(self.reactions[-1].linkColor[0],
				self.reactions[-1].linkColor[1],
				self.reactions[-1].linkColor[2],
				self.reactions[-1].linkColor[3]))
			self.canvas.before.add(self.reactions[-1].myLines)

	def changeText(self,reaction):
		if True:#len(reaction.S + reaction.P) == 2:
			if reaction.enzyme == 'default':
				reaction.boxText = 'km ' + "{0:0.1f}".format(reaction.km) + '[mM]\nVmax ' + "{0:0.1f}".format(reaction.vMax)
			else:
				reaction.boxText = str(reaction.enzyme) + '\nkm ' + "{0:0.1f}".format(reaction.km) + '[mM]\nVmax ' + "{0:0.1f}".format(reaction.vMax)+'[mM/s]'
		else:
			print('WARNING: REACTION TYPE NOT DEFINED')

	def setReactionData(self,reaction):

		box = BoxLayout()	
		if True:#(len(reaction.S) == 1 and len(reaction.P) == 1): #A->B reaction

			def on_inputKm(instance, value):
				try:
					convertedVal = float(value)
				except:
					convertedVal = reaction.km
				reaction.km = convertedVal
				self.changeText(reaction)

			def on_inputVmax(instance, value):
				try:
					convertedVal = float(value)
				except:
					convertedVal = reaction.vMax
				reaction.vMax = convertedVal
				self.changeText(reaction)

			def on_inputEnzyme(instance, value):
				reaction.enzyme = value
				self.changeText(reaction)

			inputEnzyme = TextInput(hint_text='Enzyme',multiline=False)
			inputKm = TextInput(hint_text='KM [mM]',multiline=False, input_filter = 'float')
			inputVmax = TextInput(hint_text='Vmax [mM/s] ', multiline=False, input_filter = 'float')

			inputEnzyme.bind(text=on_inputEnzyme)
			inputKm.bind(text=on_inputKm)
			inputVmax.bind(text=on_inputVmax)

			box.add_widget(inputEnzyme)
			box.add_widget(inputKm)
			box.add_widget(inputVmax)

			##Standard procedures (put outside if)
			btn1 = Button(text='Done')
			box.add_widget(btn1)
			myPopup = ReactionPopup(content = box, auto_dismiss=False, size_hint = (.5,None))

			btn1.bind(on_press = myPopup.dismiss)
				
			myPopup.open()
			self.changeText(reaction)

	def iChangeText(self,iBox):
		text = ''
		if iBox.rType == 'c':
			text = 'Competitive'
		elif iBox.rType == 'uc':
			text = 'Uncompetitive'
		elif iBox.rType == 'nc':
			text = 'Non-competitive(mixed)'

		iBox.iBoxText = 'ki ' + "{0:0.1f}".format(iBox.ki) + '[mM]\n' + text

	def setInhibitionData(self,iBox):
		box = BoxLayout()
		options = ('Competitive','Uncompetitive','Non-competitive(mixed)')


		def on_inputKi(iBox, instance, value):
			try:
				convertedVal = float(value)
			except:
				convertedVal = iBox.ki
			iBox.ki = convertedVal
			self.iChangeText(iBox)

		def on_rType(instance, value):
			text = value
			if text == 'Competitive':
				iBox.rType = 'c'
			elif text == 'Uncompetitive':
				iBox.rType = 'uc'
			elif text == 'Non-competitive(mixed)':
				iBox.rType = 'nc'
			self.iChangeText(iBox)

		spinner = Spinner(text='Select reaction type',values=options, background_color = (255,255,255,1), font_size = 12, color = (0,0,0,1))
		
		inputKi = TextInput(hint_text='Ki[mM]',multiline=False, input_filter = 'float')

		inputKi.bind(text=partial(on_inputKi,iBox))

		spinner.bind(text=on_rType)

		box.add_widget(spinner)
		box.add_widget(inputKi)

		btn1 = Button(text='Done')
		box.add_widget(btn1)
		myPopup = InhibitionPopup(content = box, auto_dismiss=False, size_hint = (.5,None), nameI = iBox.I.name)

		btn1.bind(on_press = myPopup.dismiss)
			
		myPopup.open()
		self.iChangeText(iBox)

	def on_touch_down(self, touch):
		if touch.button == 'left':
			for compound in self.compounds:
				compound.dFromClick = [touch.x - compound.center[0], touch.y - compound.center[1]]

			if self.collide_point(*touch.pos) and not self.blocked and not self.deletingNodes:
				for child in self.children:
					try:
						if child.isclicked(touch):	
							return super(NodeCanvas, self).on_touch_down(touch)			
					except AttributeError:	
						print('WARNING: Clicked element not defined')
				touch.grab(self)
				return True

	def on_touch_move(self, touch):
		if touch.grab_current is self and not self.settingS and not self.settingP and not self.deletingNodes:
			self.movingCanvas = '1'
			for compound in self.compounds:
				compound.center=[touch.x - compound.dFromClick[0], touch.y - compound.dFromClick[1]]
				compound.updateReactions()
				#for k in range(2):
					#compound.pos[k] -= (touch.pos[k]-self.dFromClick[k])*0.1

	def unblockCanvas(self,*args):
		self.blocked = False
				
	def on_touch_up(self, touch):
		if touch.button == 'left':

			if self.firstTouch: #This removes the information helpers
				self.firstTouch = False
				self.remove_widget(self.children[0]) #WARNING, BLIND SELECTION TO REMOVE ADVICE WIDGET	

			if self.collide_point(*touch.pos) and not self.blocked and not self.deletingNodes and self.movingCanvas == '0':
				for child in self.children:
					try:
						if child.isclicked(touch):
							return super(NodeCanvas, self).on_touch_down(touch)
					except AttributeError:
						print('WARNING: Clicked element not defined')
				self.pressed = touch.pos
				return True

			if self.movingCanvas == '1':
				self.movingCanvas = '2' 
			elif self.movingCanvas == '2':
				self.movingCanvas = '0'

			return super(NodeCanvas, self).on_touch_down(touch)

	def printCompounds(self):
		print('#####COMPOUNDS######')
		for compound in self.compounds:
			print(compound.name)
		print('-----------------')

	def printReactions(self):	
		print('#####REACTIONS######')
		for reaction in self.reactions:
			print('From: ')
			for element in reaction.S:
				print(element.name)
			print('To: ')
			for element in reaction.P:
				print(element.name)	
			print('Inhibited by: ')
			for element in reaction.I:
				print(element.name)				
		print('-----------------')

	def on_pressed(self, instance, pos):

		if pos[0] - 50 < self.pos[0]:
			pos = (self.pos[0] + 50, pos[1])


		self.compounds.append(GraphNode(
			center=pos,
			size_hint=(None,None)))

		self.add_widget(self.compounds[-1])
		self.compounds[-1].size = self.compounds[0].size if self.compounds else defaultNodeSize

		self.setNodeData(self.compounds[-1])
		#self.printCompounds()
		#self.printReactions()

	def setNodeData(self,compound):

		def on_textName(instance, value):
			compound.name = value

		def on_textC(instance, value):
			try:
				convertedVal = float(value)
			except:
				convertedVal = compound.c
			compound.c = convertedVal

		def on_special(instance, value):
			text = value
			if text == 'none':
				compound.special = 'none'
				compound.c = 1
			elif text == 'Infinite Source/Sink':
				compound.special = 'sourceSink'
				compound.c = 0
			self.onCchange()
			compound.changeFillColor()


		options = ['none','Infinite Source/Sink']

		spinner = Spinner(text='Select special propierties',values=options, background_color = (255,255,255,1), font_size = 12, color = (0,0,0,1))

		box = BoxLayout()
		inputName = TextInput(hint_text='Name',multiline=False)
		inputC = TextInput(hint_text='Concentration[mM]', multiline=False, input_filter = 'float')

		inputName.bind(text=on_textName)
		inputC.bind(text=on_textC)
		spinner.bind(text=on_special)

		box.add_widget(inputName)
		box.add_widget(inputC)
		box.add_widget(spinner)

		btn1 = Button(text='Done')
		box.add_widget(btn1)
		myPopup = NodePopup(content = box, auto_dismiss=False)
		btn1.bind(on_press = myPopup.dismiss)

		self.onCchange()

		myPopup.open()

	def removeNodeFromList(self,node):
		###REMOVE MY NODE OF LIST###
		self.compounds.remove(node)
		self.removeAssociatedNodeReactions(node)
		self.onCchange()

	def removeInhibition(self,reaction,ibox):
		ibox.myInhibitionLines.clear()
		self.remove_widget(ibox)
		reaction.I.remove(ibox.I)
		reaction.iBoxes.remove(ibox)

	def removeReaction(self,reaction):
		#for ibox in reaction.iBoxes:
			#removeInhibition(ibox)
		reaction.myLines.clear()		
		#reaction.canvas.clear()
		self.remove_widget(reaction)
		self.reactions.remove(reaction)
		self.updateFillColor(reaction)
		
	def updateFillColor(self,reaction):
		allElements = reaction.S + reaction.P
		if len(allElements) > 2:
			for element in allElements:
				element.changeFillColor()
		else:
			#return
			for element in allElements:
				element.fillColor = defaultFillColor

	def removeAssociatedNodeReactions(self,node):
		###REMOVE ASSOCIATED REACTIONS###
		for reaction in self.reactions:
			self.updateFillColor(reaction) #Not optimized, checks all reactions
			for element in (reaction.S + reaction.P + reaction.I):
				if element == node:
					for ibox in reaction.iBoxes:
						self.remove_widget(ibox)
						ibox.myInhibitionLines.clear()
					reaction.myLines.clear()
					reaction.iBoxes.clear()
					#reaction.canvas.clear()
					self.remove_widget(reaction)
		self.reactions[:] = [reaction for reaction in self.reactions if not node in (reaction.S + reaction.P + reaction.I)]

		self.printCompounds()
		self.printReactions()

	def removeAllNodes(self):
		print('REMOVING ALL NODES')
		for compound in self.compounds:
			self.removeAssociatedNodeReactions(compound)
			self.remove_widget(compound)
		self.compounds.clear()
		self.printCompounds()
		self.printReactions()
		self.onCchange()		

	def returnPoints(self, fromNodeX,fromNodeY,toNodeX,toNodeY,h,w):
			with self.canvas.after:
				disX = toNodeX - fromNodeX
				disY = toNodeY - fromNodeY# - fromNode.height/2
				beta = np.arctan2(disY,disX)

				#toNodeX -= radius*np.cos(beta)
				#toNodeY -= radius*np.sin(beta)
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

				return [toNodeX,toNodeY,xU,yU,xL,yL]

class GraphNode(Label):

	name = StringProperty('Default')
	c = NumericProperty(1)
	special = OptionProperty('none', options = ['none','sourceSink'])

	deletingNodes = BooleanProperty(False)
	colorAnim = ListProperty([198/255,40/255,40/255,1])
	contextColor = ListProperty([0,0,0,1])
	fillColor = ListProperty(defaultFillColor)
	dFromClick = ListProperty([0,0])
	totalC = NumericProperty(0)
	specialEffectSize = ListProperty(5*[[0,0]])

	def __hash__(self):
		return hash(self.name)

	def __ne__(self, other):
		return not(self == other)

	def __init__(self, **kwargs):
		super(GraphNode, self).__init__(**kwargs)
		self.myId = random.random()  #For saving and exporting without singular names

	def changeFillColor(self):

		for k in range(0,3): #This averages colors. Do I have to check all reactions? (Could be optimized)
			myList = [reaction.linkColor[k] if self in (reaction.S + reaction.P) else None for reaction in self.parent.reactions]
			try:
				self.fillColor[k] = np.ma.average(np.ma.array(myList,mask=[element is None for element in myList]))	
			except ZeroDivisionError:
				print('WARNING: Division by zero when setting color')

	def on_c(self, instance, value):
		try:
			self.parent.onCchange()
		except  AttributeError as e:
			print('WARNING: Error updating total concentration. Details: '+str(e))

	def on_deletingNodes(self, *args):

		myDuration = 0.3
		anim = Animation(colorAnim = [198/255,40/255,40/255,0.3], duration = myDuration, t = 'in_out_cubic') + Animation(colorAnim = [198/255,40/255,40/255,1],duration = myDuration, t = 'in_out_cubic')
		anim.repeat = True

		anim.start(self) if self.deletingNodes else anim.stop(self)

	def on_touch_down(self, touch):
		if touch.button == 'left':
			if self.collide_point(*touch.pos):
				self.dFromClick = [touch.x - self.center[0], touch.y - self.center[1]] #Mantains center distance from cursor when moving node
				touch.grab(self)

				if touch.is_double_tap and not self.parent.deletingNodes and not self.parent.settingS and not self.parent.settingP:
					self.parent.setNodeData(self)

				###REMOVE NODE###
				if self.parent.deletingNodes:#EnzimeDynamicsApp.get_running_app().deletingNodes:
					print('DELETING NODES ON')
					self.parent.removeNodeFromList(self)
					self.parent.remove_widget(self)

				###CREATE REACTION###
				elif self.parent.settingS:
					print('touched' + str(random.random()))
					if self not in self.parent.clickedS:
						self.parent.clickedS.append(self)

					else:
						self.parent.clickedS.remove(self)

				elif self.parent.settingP:
					if self not in self.parent.clickedS:
						if self not in self.parent.clickedP:
							self.parent.clickedP.append(self)
						else:
							self.parent.clickedP.remove(self)

	def on_touch_move(self, touch):
		try:
			if touch.grab_current is self and not self.parent.settingS and not self.parent.settingP and not self.parent.deletingNodes:
				self.parent.movingNode = True
				self.center=[touch.x - self.dFromClick[0], touch.y - self.dFromClick[1]] #Mantains center distance from cursor when moving node

				if (touch.x - self.width/2 - 2) < self.parent.pos[0]:
					self.center[0] = self.parent.pos[0] + self.width/2 + 2

				self.updateReactions()

		except AttributeError as e:
			print('WARNING: Moved while deleting. Details: '+str(e))

	def updateReactions(self):
		try:		

			for reaction in self.parent.reactions:
				for moved in (reaction.S + reaction.P + reaction.I):
					if moved == self:
						
						centroidX = np.average([element.center[0] for element in (reaction.S + reaction.P)])
						centroidY = np.average([element.center[1] for element in (reaction.S + reaction.P)])
						centroidSX = np.average([element.center[0] for element in reaction.S])
						centroidSY = np.average([element.center[1] for element in reaction.S])
						centroidPX = np.average([element.center[0] for element in reaction.P])
						centroidPY = np.average([element.center[1] for element in reaction.P])

						reaction.boxPosition = (int(centroidX),int(centroidY))

						#Ensures no two boxes are superposed
						for myreaction in self.parent.reactions:
							if np.sqrt((reaction.boxPosition[0] - myreaction.boxPosition[0])**2 + (reaction.boxPosition[1] - myreaction.boxPosition[1])**2) < 0.1:
								
								beta = np.arctan2(centroidSY-centroidPY,centroidSX-centroidPX)

								myreaction.boxPosition[0] -= int(np.sin(beta) * 50)
								myreaction.boxPosition[1] -= int(np.cos(beta) * 50)
								
								reaction.boxPosition[0] += int(np.sin(beta) * 50)
								reaction.boxPosition[1] += int(np.cos(beta) * 50)
						##

						linePos = 1

						for S in reaction.S:
							reaction.myLines.children[linePos].bezier = (S.center[0],S.center[1],centroidSX,centroidSY,centroidX,centroidY)
							reaction.myLines.children[linePos].width = defaultWidth*(S.size[0]/defaultNodeSize[0])
							linePos += 2

						for P in reaction.P:
							reaction.myLines.children[linePos].bezier = (centroidX,centroidY,centroidPX,centroidPY,P.center[0],P.center[1])
							reaction.myLines.children[linePos].width = defaultWidth*(S.size[0]/defaultNodeSize[0])
							linePos += 2

							arrowPos = np.sqrt((P.center[0] - centroidX)**2 + (P.center[1] - centroidY)**2)
							arrowPos = arrowPos/(arrowPos + 50)

							if len(reaction.P) == 1:
								arrowPos = 0.4

							fromPointX,fromPointY,toPointX,toPointY = self.parent.computeBezier([centroidX,centroidY],[centroidPX,centroidPY],P.center,arrowPos)

							arrowSize = defaultArrowSize*(P.size[0]/defaultNodeSize[0])
							myPoints = self.parent.returnPoints(fromPointX,fromPointY,toPointX,toPointY,arrowSize,arrowSize/4)
							reaction.myLines.children[linePos].points=myPoints
							linePos += 2

							arrowPos -= 0.2
							fromPointX,fromPointY,toPointX,toPointY = self.parent.computeBezier([centroidX,centroidY],[centroidPX,centroidPY],P.center,arrowPos)
							myPoints = self.parent.returnPoints(fromPointX,fromPointY,toPointX,toPointY,arrowSize,arrowSize/4)
							reaction.myLines.children[linePos].points=myPoints
							linePos += 2

						centerX = centroidX
						centerY = centroidY

						
						iBoxesPos = 0

						if reaction.iBoxes:
							for I in reaction.I:

								centroidSX = np.average([element.center[0] for element in (reaction.S + [I])])
								centroidSY = np.average([element.center[1] for element in (reaction.S + [I])])
								centroidPX = np.average([element.center[0] for element in (reaction.P + [I])])
								centroidPY = np.average([element.center[1] for element in (reaction.P + [I])])
								centroidX = np.average([centerX, I.pos[0]])
								centroidY = np.average([centerY, I.pos[1]])

								disCentroidSI = np.sqrt((centroidSX - I.center[0])**2 + (centroidSY - I.center[1])**2) * 8
								disCentroidPI = np.sqrt((centroidPX - I.center[0])**2 + (centroidPY - I.center[1])**2) * 8
								disCentroidI = np.sqrt((centroidX - I.center[0])**2 + (centroidY - I.center[1])**2) / 64

								sumOfDis = disCentroidSI + disCentroidPI + disCentroidI




								if I in reaction.S or I in reaction.P: 

									vectXmiddle = I.pos[0]+(centerX - I.pos[0])*4/5
									vectYmiddle = I.pos[1]+(centerY - I.pos[1])*4/5

									vectX = centerX - vectXmiddle
									vectY = centerY - vectYmiddle

									middlePointX = -3*vectY + vectXmiddle #In here i'm taking the perpendicular of vect
									middlePointY = 3*vectX + vectYmiddle

									disX = centerX - middlePointX
									disY = centerY - middlePointY
									beta = np.arctan2(disY,disX)											
									toX = centerX-20*np.cos(beta)
									toY = centerY-20*np.sin(beta) 

									bezzier = self.parent.computeBezier([I.center[0],I.center[1]],[middlePointX,middlePointY],[toX,toY],0.5)
									iBoxPointX = bezzier[2]
									iBoxPointY = bezzier[3]
								
								else:
									disX = centerX - centroidX
									disY = centerY - centroidY
									beta = np.arctan2(disY,disX)											
									toX = centerX-20*np.cos(beta)
									toY = centerY-20*np.sin(beta) 

									middlePointX = (centroidSX*disCentroidSI + centroidPX*disCentroidPI + centroidX*disCentroidI)/sumOfDis
									middlePointY = (centroidSY*disCentroidSI + centroidPY*disCentroidPI + centroidY*disCentroidI)/sumOfDis
									iBoxPointX = middlePointX
									iBoxPointY = middlePointY

								#middlePointX = centroidSX if disCentroidSI < disCentroidPI else centroidPX
								#middlePointY = centroidSY if disCentroidSI < disCentroidPI else centroidPY

								lineInhibitionPos = 1

								reaction.iBoxes[iBoxesPos].myInhibitionLines.children[lineInhibitionPos].bezier=(I.center[0],I.center[1],middlePointX,middlePointY,toX,toY)
								
								lineInhibitionPos += 2

								inhibitionH = defaultInhibitionH*(I.size[0]/defaultNodeSize[0])
								inhibitionW = defaultInhibitionW*(I.size[0]/defaultNodeSize[0])
								myPoints = self.parent.returnPoints(middlePointX,middlePointY,toX,toY,inhibitionH,inhibitionW)
								reaction.iBoxes[iBoxesPos].myInhibitionLines.children[lineInhibitionPos].points = myPoints

								lineInhibitionPos += 2									


								reaction.iBoxes[iBoxesPos].pos = (int(iBoxPointX - reaction.width/2), int(iBoxPointY - reaction.height/2)) #Assuming inhibition order does not change
								iBoxesPos += 1

								# toX = centerX-30*np.cos(beta)
								# toY = centerY-30*np.sin(beta)
								
								# myPoints = self.parent.returnPoints(middlePointX,middlePointY,toX,toY,0.1,5)
								# reaction.myInhibitionLines.children[lineInhibitionPos].points = myPoints
								# lineInhibitionPos += 2
		except AttributeError as e:
			print('WARNING: '+str(e))

	def on_touch_up(self, touch):
		try:
			self.parent.movingNode = False
		except:
			print('WARNING: Touching up in deletion mode')
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
	linkColor = ListProperty([0,0,0,1])

	enzyme = StringProperty('default')
	km = NumericProperty(0.5)
	vMax = NumericProperty(1.5)
	I = ListProperty([])
	iBoxes = ListProperty([])
	S = ListProperty([])
	P = ListProperty([])

	def __init__ (self,**kwargs):
		super(Reaction,self).__init__(**kwargs)
		self.myLines = InstructionGroup()
		self.linkColor = [random.random()/2+0.5,random.random()/2+0.5,random.random()/2+0.5,1]
		self.myId = random.random()  #For saving and exporting without singular names

	def isclicked(self,touch):
		if self.collide_point(*touch.pos):
			return True
		return False

	def on_touch_down(self, touch):	 #Creates Inhibition

		if self.collide_point(*touch.pos) and touch.button == 'left':

			if self.parent.deletingNodes:

				self.parent.removeReaction(self)

			else:

				if touch.is_double_tap and not self.parent.deletingNodes and not self.parent.settingS and not self.parent.settingP:
					self.parent.setReactionData(self)

				if self.parent.settingP:

					if self.parent.clickedS:

						for I in reversed(self.parent.clickedS):

							if I not in self.I:

								self.I.append(I)

								self.iBoxes.append(InhibitionPropierties(reaction = self, I = I))
								self.parent.add_widget(self.iBoxes[-1])

								self.createInhibitionLines(I)

								self.parent.setInhibitionData(self.iBoxes[-1])

						self.parent.buttonBehaviour()
						#self.parent.printCompounds()
						self.parent.printReactions()

					self.parent.clickedS.clear()
					self.parent.clickedP.clear()

	def createInhibitionLines(self,I):

		centerX = np.average([element.center[0] for element in (self.S + self.P)]) #Could be computed once (for all I), but loading code becomes larger
		centerY = np.average([element.center[1] for element in (self.S + self.P)]) #Could be computed once (for all I), but loading code becomes larger

		centroidSX = np.average([element.center[0] for element in (self.S + [I])])
		centroidSY = np.average([element.center[1] for element in (self.S + [I])])
		centroidPX = np.average([element.center[0] for element in (self.P + [I])])
		centroidPY = np.average([element.center[1] for element in (self.P + [I])])
		centroidX = np.average([centerX, I.pos[0]])
		centroidY = np.average([centerY, I.pos[1]])

		disCentroidSI = np.sqrt((centroidSX - I.center[0])**2 + (centroidSY - I.center[1])**2) * 8
		disCentroidPI = np.sqrt((centroidPX - I.center[0])**2 + (centroidPY - I.center[1])**2) * 8
		disCentroidI = np.sqrt((centroidX - I.center[0])**2 + (centroidY - I.center[1])**2) / 64

		sumOfDis = disCentroidSI + disCentroidPI + disCentroidI

		disX = centerX - centroidX
		disY = centerY - centroidY
		beta = np.arctan2(disY,disX)
		toX = centerX-20*np.cos(beta)
		toY = centerY-20*np.sin(beta)

		if I in self.S or I in self.P: 

			vectXmiddle = I.pos[0]+(centerX - I.pos[0])*4/5
			vectYmiddle = I.pos[1]+(centerY - I.pos[1])*4/5

			vectX = centerX - vectXmiddle
			vectY = centerY - vectYmiddle

			middlePointX = -3*vectY + vectXmiddle #In here i'm taking the perpendicular of vect
			middlePointY = 3*vectX + vectYmiddle

			disX = centerX - middlePointX
			disY = centerY - middlePointY
			beta = np.arctan2(disY,disX)											
			toX = centerX-20*np.cos(beta)
			toY = centerY-20*np.sin(beta) 

			bezzier = self.parent.computeBezier([I.center[0],I.center[1]],[middlePointX,middlePointY],[toX,toY],0.5)
			iBoxPointX = bezzier[2]
			iBoxPointY = bezzier[3]
		
		else:
			disX = centerX - centroidX
			disY = centerY - centroidY
			beta = np.arctan2(disY,disX)											
			toX = centerX-20*np.cos(beta)
			toY = centerY-20*np.sin(beta)
			middlePointX = (centroidSX*disCentroidSI + centroidPX*disCentroidPI + centroidX*disCentroidI)/sumOfDis
			middlePointY = (centroidSY*disCentroidSI + centroidPY*disCentroidPI + centroidY*disCentroidI)/sumOfDis
			iBoxPointX = middlePointX
			iBoxPointY = middlePointY

		self.iBoxes[-1].pos = (int(iBoxPointX - self.width/2), int(iBoxPointY - self.height/2))

		self.iBoxes[-1].myInhibitionLines.add(Line(bezier=(I.center[0],I.center[1],middlePointX,middlePointY,toX,toY),width = defaultWidth*(I.size[0]/defaultNodeSize[0])))

		inhibitionH = defaultInhibitionH*(I.size[0]/defaultNodeSize[0])
		inhibitionW = defaultInhibitionW*(I.size[0]/defaultNodeSize[0])							
		myPoints = self.parent.returnPoints(middlePointX,middlePointY,toX,toY,inhibitionH,inhibitionW)
		self.iBoxes[-1].myInhibitionLines.add(Line(points=(myPoints), width = defaultWidth*(I.size[0]/defaultNodeSize[0])))

		# toX = centerX-30*np.cos(beta)
		# toY = centerY-30*np.sin(beta)

		# myPoints = self.parent.returnPoints(middlePointX,middlePointY,toX,toY,0.1,5)
		# self.myInhibitionLines.add(Line(points=(myPoints), width = 2))				

		self.parent.canvas.before.add(Color(self.linkColor[0]-0.12,
		self.linkColor[1]-0.12,
		self.linkColor[2]-0.2,
		self.linkColor[3]))						
		self.parent.canvas.before.add(self.iBoxes[-1].myInhibitionLines)
				
class InhibitionPropierties(Label):
	reaction = ObjectProperty()
	I = ObjectProperty()
	ki = NumericProperty(1)
	rType = OptionProperty('c', options = ['none','c','uc','nc'])
	iBoxText = StringProperty('')

	def __init__ (self,**kwargs):
		super(InhibitionPropierties,self).__init__(**kwargs)
		self.myInhibitionLines = InstructionGroup()

	def isclicked(self,touch):
		if self.collide_point(*touch.pos):
			return True
		return False

	def on_touch_down(self, touch):	
		if self.collide_point(*touch.pos):
			if self.parent.deletingNodes:
				self.parent.removeInhibition(self.reaction,self)
			else:
				if touch.is_double_tap:
					self.parent.setInhibitionData(self)
				Clock.schedule_once(self.parent.unblockCanvas, 0.1)

class NodePopup(Popup):

	def on_open(self):
		pass
	def on_dismiss(self):
		#WTF, THERE HAS TO BE A CLEANER WAY SOMEHOW
		if self.parent.children[1].children[0].ids.myNodeCanvas.secondInfo:
			myInitialInstructions2 = InitialInstructions2()
			self.parent.children[1].children[0].ids.myNodeCanvas.add_widget(myInitialInstructions2) 
			self.parent.children[1].children[0].ids.myNodeCanvas.firstTouch = True
			self.parent.children[1].children[0].ids.myNodeCanvas.secondInfo = False

class ReactionHelper(BoxLayout):
	contextColor = ListProperty()

	def cancelButton(self):
		self.parent.ids.myNodeCanvas.settingS = False
		self.parent.ids.myNodeCanvas.settingP = False
		# for element in self.parent.ids.myNodeCanvas.clickedS + self.parent.ids.myNodeCanvas.clickedP:
		# 	element.canvas.remove(element.canvas.children[-1]) #ellipsis(deprecated)
		self.parent.contextText = 'Create\nReaction'
		self.parent.contextColor = defaultContextColor#[41/255, 182/255, 246/255, 1]
		for compound in self.parent.ids.myNodeCanvas.compounds:
			compound.contextColor = [0,0,0,1]
		self.parent.remove_widget(self.parent.myReactionHelper)

class ReactionPopup(Popup):

	def on_open(self):
		pass
	def on_dismiss(self):
		pass 

class ModifierPopup(Popup):
	pass	

class ResultPopup(Popup):
	pass	

class InhibitionPopup(Popup):
	nameI = StringProperty('')

class OpenDataPopup(Popup):
	pass

class SaveDataPopup(Popup):
	pass
	
class MainMenu(Screen):
	pass

class OptionsCanvas(BoxLayout):
	pass

class InitialInstructions(BoxLayout):
	pass

class InitialInstructions2(BoxLayout):
	pass

class MyScreenManager(ScreenManager):
	pass

class mySettingsInterface(InterfaceWithNoMenu):  
    pass

class mySettings(Settings):  
	
	def __init__(self, **kwargs):
		super(mySettings, self).__init__(**kwargs)
		#self.register_type('title', mySettingTitle)

class mySettingTitle(Label):  
    title = Label.text

class EnzymeDynamicsNewApp(App): 
	icon = 'img/ico.png'
	title = 'Enzyme Dynamics'
	settings_cls = mySettings

	def applyConfig(self):
		for key in ['tmax','dt']:
			value = self.config.get('ODEsettings',key)
			setattr(self.root.children[0].ids.myNodeCanvas,key,float(value))

	def build(self):
		#root = Builder.load_file('enzymedynamics.kv')
		#self.use_kivy_settings = False
		return MyScreenManager() #root

	def build_config(self,config):
		config.setdefaults('ODEsettings',{
			'tmax': 2,
			'dt': 0.01,
			})
	def build_settings(self,settings):
		#with open("settings.json", "r") as settings_json:
			#settings.add_json_panel('My settings', self.config, data=settings_json.read())
		settings.add_json_panel('Settings', self.config, data=settings_json)

	def on_config_change(self, config, section, key, value):
		
		if section == 'ODEsettings':
			setattr(self.root.children[0].ids.myNodeCanvas,key,float(value))

		else:
			print(key,value)

if __name__ == "__main__":
	EnzymeDynamicsNewApp().run()