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

__version__ = '0.1'

spanish_strings = {
	'title' : 'RanABC',
	'file'	: 'Archivo',
	'grade' : 'Nivel',
	'difficulty' :  'Dificultad',
	'start' : 'Iniciar',
	'letsspell' : '¡A deletrear!',
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
	total_words = NumericProperty()
	accent_type = StringProperty()
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
		print('next word is %s' % next_word.word)
		self.word = next_word.word
		self.definition = next_word.definition
		self.sentence1 = next_word.sentence1
		self.sentence2 = next_word.sentence2
		self.level = '%s - %s' % (next_word.grade, next_word.level.title())
		self.shuffling = False
		self.ids['lbl_word'].color = [0,0,0,1]
		self.accent_type = next_word.type


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
	language = OptionProperty("Español", options=["Español", "English"])
	strings = DictProperty(spanish_strings)
	word_count = StringProperty()
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
			if not self.sel_mode or self.sel_mode=='Random':
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

	def clear_db(self):
		self.db = parse_tools.WordCollection()
		self.update_word_count(self.db.get_word_count())

if '__main__' == __name__:
	db = parse_tools.WordCollection()
	fn = '../assets/words.xlsx'
	if os.path.exists(fn):
		parse_tools.parse_wordlist(db, fn)
	Config.set('graphics', 'fullscreen', 'auto')

	app = MainApp()
	app.db = db
	app.run()
