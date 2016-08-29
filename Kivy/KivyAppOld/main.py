from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse, Line


from kivy.uix.button import Button
from kivy.lang import Builder


class MapMenuForm(BoxLayout):
	pass


class NewMap(BoxLayout):
	pass

class Map(BoxLayout):
	def new_enzyme(self):
		pass
	

class OdenzymeRoot(BoxLayout):
	def to_new_map(self):
		self.clear_widgets()
		self.add_widget(NewMap())

class OdenzymeApp(App):
	pass

if __name__ == '__main__':
		OdenzymeApp().run()