#!/usr/bin/python

from openpyxl import load_workbook
#from BaseItems import Word
from collections import namedtuple
from itertools import zip_longest

Word = namedtuple('Word',['level','grade','word','definition','sentence1','sentence2','type'])

def parse_wordlist(db, f):
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
		db.add_word(w)
	print("parsed %s words from file %s" % (len(db.keys()),f))
	return db

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

word_db = WordCollection()

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
	if app.sel_level:
		level = app.sel_level
	else:
		level = ''
	w = {
		'word' 			: app.get_string('get_ready'),
		'grade'			: app.sel_grade,
		'level'			: app.sel_level,
		'definition'	: app.get_grade_name(),
		'sentence1'		: app.get_string('level_words') % level,
		'sentence2'		: '',
		'type'			: ''
	}
	return Word(**w)

if __name__=='__main__':
	word_db.add_word(sample_word())
	parse_wordlist(word_db, 'bee16.xlsx')
