#!/usr/bin/python

from openpyxl import load_workbook
#from BaseItems import Word
from collections import namedtuple

Word = namedtuple('Word',['level','grade','word','definition','sentence1','sentence2'])

def parse_wordlist(f):
	word_list = []
	wb = load_workbook(f)
	ws = wb.active
	for row in ws:
		w = Word._make([unicode(v.value) for v in row])
		word_db.add_word(w)
	return word_list

class WordCollection(dict):
	classified_words = {}

	def add_word(self, word):
		if not isinstance(word, Word):
			raise Exception('not a Word!')
		k = self._generate_key(word)
		self[k] = word
		if word.grade not in self.classified_words:
			self.classified_words[word.grade] = {}
		if word.level not in self.classified_words[word.grade]:
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



	def _generate_key(self, word):
		return '{0}_{1}_{2}'.format(word.word, word.grade, word.level).lower()

word_db = WordCollection()

def sample_word():
	w = {
		'word' 			: 'word',
		'grade'			: '1',
		'level'			: 'easy',
		'definition'	: 'a single distinct meaningful element of speech or writing',
		'sentence1'		: 'My favorite word is word.',
		'sentence2'		: 'I have so many words.'
	}
	return Word(**w)

def get_ready_word():
	w = {
		'word' 			: 'Get Ready!',
		'grade'			: '',
		'level'			: '',
		'definition'	: '',
		'sentence1'		: '',
		'sentence2'		: ''
	}
	return Word(**w)

if __name__=='__main__':
	word_db.add_word(sample_word())
	parse_wordlist('bee16.xlsx')
