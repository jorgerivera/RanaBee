#!/usr/bin/python

from openpyxl import load_workbook
#from BaseItems import Word
from collections import namedtuple
from itertools import zip_longest
import copy
import json
import os
import random
from hashlib import md5

from json import JSONEncoder

def _default(self, obj):
	return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder().default
JSONEncoder.default = _default

#Word = namedtuple('Word',['level','grade','word','definition','sentence1','sentence2','type'])

class Word(object):

	_fields = ['level','grade','word','definition','sentence1','sentence2','type']

	@property
	def level(self):
		return self.__level

	@level.setter
	def level(self, val):
		self.__level = val

	@property
	def grade(self):
		return self.__grade

	@grade.setter
	def grade(self, val):
		self.__grade = val

	@property
	def word(self):
		return self.__word

	@word.setter
	def word(self, val):
		self.__word = val

	@property
	def definition(self):
		return self.__definition

	@definition.setter
	def definition(self, val):
		self.__definition = val

	@property
	def sentence1(self):
		return self.__sentence1

	@sentence1.setter
	def sentence1(self, val):
		self.__sentence1 = val

	@property
	def sentence2(self):
		return self.__sentence2

	@sentence2.setter
	def sentence2(self, val):
		if val==None or val=='None':
			self.__sentence2 = None
		else:
			self.__sentence2 = val

	@property
	def type(self):
		return self.__type

	@type.setter
	def type(self, val):
		if val==None or val=='None':
			self.__type = None
		else:
			self.__type = val
	
	def __init__(self, *wargs, **kwargs):
		for k,v in kwargs.items():
			setattr(self, k, v)

	def __repr__(self):
		values = {}
		for k in self._fields:
			values[k] = getattr(self, k)
		return json.dumps(values)

	def to_json(self):
		values = {}
		for k in self._fields:
			values[k] = getattr(self, k)
		return values


def parse_wordlist(f, db=None, wlist=None):
	wb = load_workbook(f)
	ws = wb.active
	first = True
	for row in ws:
		if first:
			first = False
			continue
		if not row[0].value or row[0].value == 'dificultad':
			continue
		row[0].value = row[0].value.lower()
		values = [str(v.value).replace(u'\xa0',' ').strip() for v in row[0:7]]
		word_dict = { k:v for k,v in zip_longest(Word._fields, values)}
		w = Word(**word_dict)
		if db is not None:
			db.add_word(w)
		if wlist is not None:
			wlist.add_word(w)
	if db is not None:
		print(f"parsed {len(db.keys())} words from file {f}")
		return db
	if wlist is not None:
		print(f"parsed {len(wlist)} words from file {f}")
		return wlist

class WordCollection(dict):

	def __init__(self, *wargs, **kwargs):
		dict.__init__(self, *wargs, **kwargs)
		self.classified_words = {}

	def add_word(self, word):
		if not isinstance(word, Word):
			raise Exception('not a Word!')
		k = self._generate_key(word)
		self[k] = word
		if word.grade not in self.classified_words:
			print("new grade %s", word.grade)
			self.classified_words[word.grade] = {}
		if word.level not in self.classified_words[word.grade]:
			print("new level %s-%s", word.grade, word.level)
			self.classified_words[word.grade][word.level] = []
		self.classified_words[word.grade][word.level].append(k)

	def get_word_list(self, grade=None, level=None):
		grade_list = []
		if not grade or grade in self.classified_words:
			grade_list = self.classified_words.keys() if not grade else [ grade ]

		word_key_list = []
		for g in grade_list:
			this_grade_levels = self.classified_words[g].keys() if not level else [level]
			for l in this_grade_levels:
				word_key_list += self.classified_words[g].get(l,[])

		word_key_list.sort(reverse=True)

		return word_key_list

	def get_levels(self):
		level_list = set()
		for grade in self.classified_words.keys():
			for level in self.classified_words[grade].keys():
				level_list.add(level)
		print('DB get levels %s', level_list)
		return level_list

	def get_grades(self):
		grade_list = set()
		for grade in self.classified_words.keys():
			grade_list.add(grade)
		return sorted(grade_list)

	def get_word_count(self):
		return len(self.keys())

	def _generate_key(self, word):
		return u'{0}_{1}_{2}'.format(word.word, word.grade, word.level).lower()

class WordList(list):

	def __init__(self, *wargs, **kwargs):
		list.__init__(self, *wargs, **kwargs)
		self._unique_grades = None
		self._unique_levels = None

	def add_word(self, word):
		if not isinstance(word, Word):
			raise Exception('not a Word!')
		self.append(word)

	def get_levels(self):
		if not self._unique_levels:
			all_levels = [ w.level for w in self ]
			self._unique_levels = set(all_levels)
			print(f"Refreshed unique levels {self._unique_levels}")
		return self._unique_levels

	def get_grades(self):
		if not self._unique_grades:
			all_grades = [ w.grade for w in self ]
			self._unique_grades = sorted(set(all_grades))
			print(f"Refreshed unique grades {self._unique_grades}")
		return self._unique_grades

	def refresh_grades_and_levels(self):
		self._unique_grades = None
		self._unique_levels = None

	def get_word_count(self):
		# Consider just using len() instead
		return len(self)

	def get_word_list(self, grade=None, level=None):
		if not grade:
			sel_grades = self.get_grades()
		else:
			sel_grades = [ grade ]

		if not level:
			sel_levels = self.get_levels()
		else:
			sel_levels = [ level ]
		
		return [ w for w in self if (w.level in sel_levels and w.grade in sel_grades) ]

	def randomize(self):
		random.shuffle(self)

	def hash(self):
		return md5(repr(self).encode('utf-8')).hexdigest()

	def __repr__(self):
		return json.dumps(self)


class ContestState(dict):

	@property
	def words(self):
		return self['words']

	@words.setter
	def words(self, val):
		if isinstance(val, WordList):
			self['words'] = copy.deepcopy(val)
		elif isinstance(val, list) and isinstance(val[0], dict) :
			print('setting words from a list of dicts')
			self['words'] = WordList()
			for w in val:
				print(w)
				next_word = Word(**w)
				print(f"WORD: {next_word.word}" )
				self['words'].add_word(next_word)
		else:
			raise Exception('Not a WordList or a List')

	@property
	def sel_words(self):
		return self['sel_words']

	@sel_words.setter
	def sel_words(self, val):
		self['sel_words'] = val

	@property
	def sel_level(self):
		return self['sel_level'] if 'sel_level' in self else None
	
	@sel_level.setter
	def sel_level(self, val):
		self['sel_level'] = val

	@property
	def sel_grade(self):
		return self['sel_grade'] if 'sel_grade' in self else None
	
	@sel_grade.setter
	def sel_grade(self, val):
		self['sel_grade'] = val

	def __init__(self, *wargs, **kwargs):
		dict.__init__(self, *wargs, **kwargs)

	def save_file(self, filename):
		with open(filename,'w') as f:
			f.write(json.dumps(self, indent=2))

	def load_file(self, filename):
		try:
			with open(filename,'r') as f:
				from_file = json.load(f)
		except Exception as e:
			print(f"Could not read file {filename}: {e}")
			return
		print(f"recovered {len(from_file['words'])} from {filename}")
		self.sel_grade = from_file['sel_grade']
		self.sel_level = from_file['sel_level']
		self.words = from_file['words']
		self.sel_words = self.words.get_word_list(grade=self.sel_grade, level=self.sel_level)
		self.print_info()

	def clear_file(self, filename):
		print("Contest done! Remove state file!")
		os.remove(filename)

	def print_info(self):
		print(f'State data:')
		print(f'  Selected grade {self.sel_grade}')
		print(f'  Selected level {self.sel_level}')
		print(f'  Word count  {len(self.words)}')
		print(f'  Selected words {len(self.sel_words)}')


word_db = WordCollection()
word_list = WordList()

def sample_word():
	w = {
		'word' 			: 'word',
		'grade'			: '1',
		'level'			: 'easy',
		'definition'	: 'a single distinct meaningful element of speech or writing',
		'sentence1'		: 'My favorite word is word.',
		'sentence2'		: 'I have so many words.',
		'type'			: 'Simple word'
	}
	return Word(**w)

def get_ready_word(app):
	if app.state.sel_level:
		level = app.state.sel_level
	else:
		level = ''
	w = {
		'word' 			: app.get_string('get_ready'),
		'grade'			: app.state.sel_grade,
		'level'			: app.state.sel_level,
		'definition'	: app.get_grade_name(),
		'sentence1'		: app.get_string('level_words') % level,
		'sentence2'		: '',
		'type'			: ''
	}
	return Word(**w)

if __name__=='__main__':
	word_list = parse_wordlist('assets/bee22.xlsx', wlist=word_list)
	wl = word_list
