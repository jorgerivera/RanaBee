#!/usr/bin/python
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.factory import Factory
from kivy.properties import StringProperty, ObjectProperty, ListProperty, \
	NumericProperty, OptionProperty, DictProperty
from kivy.resources import resource_find
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.clock import Clock
from kivy.config import Config

import parse_tools
import random
from os.path import sep, expanduser, isdir, dirname
import os.path
import time
from functools import partial
import sys
sys.path.insert(0, "../")

sw = parse_tools.sample_word()

__version__ = '0.2'

spanish_strings = {
	'title' : 'RanABC',
	'file'	: 'Archivo',
	'grade' : 'Nivel',
	'difficulty' :  'Dificultad',
	'start' : '¡Iniciar!',
	'letsspell' : '¡A deletrear!',
	'random' : 'Aleatorio',
	'alphabetic' :  'Alfabético',
	'definition' : 'Definición:',
	'samples' : 'Ejemplos:',
	'cancel' : 'Cancelar',
	'load' : 'Cargar',
	'new' : 'Nuevo',
	'open' : 'Abrir',
	'quit' : 'Salir',
	'no_words' : 'No hay palabras cargadas',
	'words_loaded' : 'Hay %s palabras cargadas',
	'accent_type' : 'Acento:',
	'get_ready' : '¡Prepárense!',
	'words_selected' : 'Hay %s palabras seleccionadas',
	'no_words_selected' : 'No hay palabras seleccionadas',
	'level_list' : ['mediana', 'dificil', 'experto'],
	'grade_list' : ['No', 'Primer', 'Segundo', 'Tercer', 'Cuarto', 'Quinto', 'Sexto'],
	'grade_name' : '%s grado',
	'next_level' : '¡Siguiente dificultad!',
	'next_grade' : '¡Siguiente nivel!',
	'the_end'    : '¡Fin!',
	'level_words': '¡Siguen las palabras de dificultad %s!',
}

english_strings = {
	'title' : 'Spelling Bee',
	'file'	: 'File',
	'grade' : 'Grade',
	'difficulty' :  'Difficulty',
	'start' : 'Start!',
	'letsspell' : 'Let\'s spell!',
	'random' : 'Random',
	'alphabetic' :  'Alphabetic',
	'definition' : 'Definition:',
	'samples' : 'Examples:',
	'cancel' : 'Cancel',
	'load' : 'Load',
	'new' : 'New',
	'open' : 'Open',
	'quit' : 'Quit',
	'no_words' : 'No words loaded',
	'words_loaded' : '%s words loaded',
	'accent_type' : 'Accent:',
	'get_ready' : 'Get Ready!',
	'words_selected' : '%s words selected',
	'no_words_selected' : 'No words selected',
	'level_list' : ['easy', 'medium', 'difficult', 'challenge'],
	'grade_list' : ['No', 'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth'],
	'grade_name' : '%s grade',
	'next_level' : 'Next level!',
	'next_grade' : 'Next grade!',
	'the_end'    : 'Done!',
	'level_words': 'Starting with %s words!',
}

class ImageButton(ButtonBehavior, Image):
	pass

Factory.register('ImageButton',cls=ImageButton)

class RootWidget(Screen):
	'''This is the class representing your root widget.
	   By default it is inherited from BoxLayout,
	   you can use any other layout/widget depending on your usage.
	'''
	pass

class CardWidget(Screen):
	w = ObjectProperty(sw)
	word = StringProperty()
	definition = StringProperty()
	sentence1 = StringProperty()
	sentence2 = StringProperty()
	level = StringProperty()
	language = None
	total_words = NumericProperty()
	word_size = NumericProperty()
	accent_type = StringProperty()
	accent_lbl = StringProperty()
	shuffling = False

	def update_boxes(self, *args):
		print('updating boxes on card widget! [%s]' % len(App.get_running_app().sel_words))
		boxes = self.ids['boxes']
		boxes.clear_widgets()
		for i in range(self.total_words):
			if i < len(App.get_running_app().sel_words):
				boxes.add_widget(Button(background_color=[0,1,0,1]))
			else:
				boxes.add_widget(Button(background_color=[1,0,0,1]))

	def on_pre_enter(self):
		self.update_boxes()
		self.change_word(parse_tools.get_ready_word(App.get_running_app()))

	def on_pre_leave(self):
		Clock.unschedule(self.shuffle_words)

	def next_word(self):
		self.ids['lbl_word'].color = [0.7,0.7,0.7,1]
		secs = min(1.5, 0.06 * len(App.get_running_app().sel_words))
		Clock.schedule_once(self.set_new_word, secs)
		Clock.schedule_interval(self.shuffle_words, 0.05)
		self.shuffling = True

	def set_new_word(self, *args):
		try:
			next_key = App.get_running_app().sel_words.pop()
			Clock.schedule_once(partial(self.change_word, db[next_key]))
			Clock.schedule_once(self.update_boxes)
		except IndexError:
			App.get_running_app().root.ids.sm.current = 'root'

	def shuffle_words(self, *args):
		if not self.shuffling:
			Clock.unschedule(self.shuffle_words)
			return
		self.definition = ''
		self.sentence1 = ''
		self.sentence2 = ''
		self.level = ' - '
		self.accent_type = ''
		if len(App.get_running_app().sel_words) > 0:
			word_key = random.choice(App.get_running_app().sel_words)
			self.word = App.get_running_app().db[word_key].word

	def change_word(self, next_word, *largs):
		print('next word is %s [has %s chars]' % (next_word.word, len(next_word.word)))
		self.word = next_word.word
		if len(next_word.word) > 25:
			self.word_size = 80
		elif len(next_word.word) > 18:
			self.word_size = 100
		else:
			self.word_size = 120
		self.definition = next_word.definition
		self.sentence1 = next_word.sentence1
		self.sentence2 = next_word.sentence2
		self.level = '%s - %s' % (next_word.grade, next_word.level.title())
		self.shuffling = False
		self.ids['lbl_word'].color = [0,0,0,1]
		if next_word.type and next_word.type!='None':
			self.accent_type = next_word.type
			self.accent_lbl = App.get_running_app().get_string("accent_type")
		else:
			self.accent_type = ""
			self.accent_lbl = ""


class LoadDialog(FloatLayout):
	load = ObjectProperty(None)
	cancel = ObjectProperty(None)

class MainApp(App):
	'''This is the main class of your app.
	   Define any app wide entities here.
	   This class can be accessed anywhere inside the kivy app as,
	   in python::

		 app = App.get_running_app()
		 print (app.title)

	   in kv language::

		 on_release: print(app.title)
	   Name of the .kv file that is auto-loaded is derived from the name
	   of this class::

		 MainApp = main.kv
		 MainClass = mainclass.kv

	   The App part is auto removed and the whole name is lowercased.
	'''
	sel_grade = StringProperty()
	sel_level = StringProperty()
	sel_words = ListProperty()
	sel_mode = StringProperty()
	loadfile = ObjectProperty(None)
	language = OptionProperty("English", options=["Español", "English"])
	strings = DictProperty(english_strings)
	word_count = StringProperty()
	sel_word_count = StringProperty()
	sp_levels = ListProperty()
	sp_grades = ListProperty()
	db = parse_tools.word_db

	def build(self):
		#parse_tools.parse_wordlist(resource_find('bee14.xlsx'))
		self.root.ids.sm.add_widget(RootWidget(name='root'))
		self.root.ids.sm.add_widget(CardWidget(name='card'))
		#self.strings = spanish_strings
		self.update_word_count(self.db.get_word_count())
		self.sp_levels = self.db.get_levels()
		self.sp_grades = self.db.get_grades()

#	def build_config(self, config):
#		config.set('graphics',
#			'window_state', 'maximized')

	def open_card(self):
		print(self.sel_grade, self.sel_level)
		self.sel_words = self.db.get_word_list(grade=self.sel_grade,
							level=self.sel_level)
		print(self.sel_words)
		self.root.ids.sm.get_screen('card').total_words = len(self.sel_words)
		if any(self.sel_words):
			if not self.sel_mode or self.sel_mode==self.get_string('random'):
				random.shuffle(self.sel_words)
			self.root.ids.sm.current = 'card'
		else:
			print('no words like this!')

	def load(self, path, filename):
		print('path [%s] fn [%s]' % (path, filename))
		if os.path.exists(filename[0]):
			f = filename[0]
		else:
			f = os.path.join(path, filename[0])
		if os.path.exists(f):
			try:
				parse_tools.parse_wordlist(self.db, resource_find(f))
				self.update_word_count(self.db.get_word_count())
			except:
				print('failed loading file')
		else:
			print('file not found')
		self.dismiss_popup()

	def back(self):
		sm = self.root.ids.sm
		if sm.current == 'card':
			sm.current = sm.previous()
		else:
			pass

	def dismiss_popup(self):
		self._popup.dismiss()

	def open_file(self):
		print('clicked on open')
		content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
		self._popup = Popup(title="Load file", content=content,
			size_hint=(0.9, 0.9))
		self._popup.open()

	def get_string(self, key):
		if self.strings.has_key(key):
			return self.strings[key]
		else:
			return key

	def update_word_count(self, count):
		if count > 0:
			self.word_count = self.get_string('words_loaded') % count
		else:
			self.word_count = self.get_string('no_words')
		self.sp_levels = self.db.get_levels()
		self.sp_grades = self.db.get_grades()

	def update_selected_words(self):
		# Show selected words, according to values from spinners
		self.sel_words = self.db.get_word_list(grade=self.sel_grade,
							level=self.sel_level)
		count = len(self.sel_words)
		if not self.sel_mode or self.sel_mode==self.get_string('random'):
			random.shuffle(self.sel_words)
		if count > 0:
			self.sel_word_count = self.get_string('words_selected') % count
		else:
			self.sel_word_count = self.get_string('no_words_selected')

	def clear_db(self):
		self.db = parse_tools.WordCollection()
		self.update_word_count(self.db.get_word_count())

	def set_grade(self, text):
		self.sel_grade = text
		self.update_selected_words()

	def set_level(self, text):
		self.sel_level = text
		self.update_selected_words()


if '__main__' == __name__:
	db = parse_tools.WordCollection()
	fn = 'assets/ranabc17.xlsx'
	if os.path.exists(fn):
		parse_tools.parse_wordlist(db, fn)
	Config.set('graphics', 'fullscreen', 'auto')

	app = MainApp()
	app.db = db
	app.run()
