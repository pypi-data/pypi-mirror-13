import json
from gensim import corpora, models
import time
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
import anticontract
import pickle

class ReviewTokenizer:
	"""Build a list of tokens for the given review(s) """

	stop_en = get_stop_words('en')
	tokenizer = RegexpTokenizer(r'\w+')

	def __init__(self, reviews):
		self.tokenized_docs = {}
		self.reviews = reviews

	def tokenize(self):				
		print 'Tokenizing reviews.\n'
		for doc in self.reviews:
			raw_doc = doc['text'].replace("w/", "")
			raw_doc = raw_doc.replace("\n", "")
			doc_lower = raw_doc.lower()
			doc_final = anticontract.expand_contractions(doc_lower)
			tokens = self.tokenizer.tokenize(doc_final)
			clean_tokens = [token for token in tokens if token not in self.stop_en]
			self.tokenized_docs[doc['review_id']] = {'tokens': clean_tokens, 'user': doc['user_id']}
		print 'Done tokenizing reviews.\n'
	
	def save(self, fileName):		
		print 'Saving tokenized reviews to file ', fileName, '.\n'
		with open(fileName + '.json','w') as f:
			json.dump(self.tokenized_docs,f)
		print 'Done saving tokenized reviews.\n'


class DictionaryBuilder:
	"""Build dictionary that assigns an id to each unique token. Used for building the document-term-matrix."""

	def __init__(self, tokDocs):
		self.tokDocs = tokDocs

	def build(self):
		self.srcTexts = []
		print "Building dictionary.\n"
		for value in self.tokDocs.itervalues():
			self.srcTexts.append(value['tokens'])
		self.dictionary = corpora.Dictionary(self.srcTexts)
		print 'Done building dictionary.\n'

	def save(self, fileNameDict):
		print 'Saving dictionary.\n'
		self.dictionary.save(fileNameDict + '.dict')
		print 'Done saving dictionary.\n'

class DTMBuilder:
	"""Builds a document-term-matrix from a given dictionary of id-token pairs"""

	def __init__(self, dictionary, srcTexts):
		self.dictionary = dictionary
		self.srcTexts = srcTexts
		self.dtm = []

	def build(self):
		print 'Building document-term-matrix.\n'
		self.dtm = [self.dictionary.doc2bow(text) for text in self.srcTexts]
		print 'Done building document-term-matrix.\n'

	def save(self,fileName):
		print 'Saving document-term-matrix.\n'
		with open(fileName + '.json','w') as f:
			pickle.dump(self.dtm,f)
		print 'Done saving document-term-matrix.\n'

class LDAWrapper:
	"""Wrapper class for easy use of LDA algorithm as given in gensim package"""

	def __init__(self, dtm, dictionary):
		self.dtm = dtm
		self.dictionary = dictionary

	def run(self, num_topics = 100, passes = 20):
		print 'Fitting LDA model.\n'
		self.ldamodel = models.ldamodel.LdaModel(self.dtm, num_topics = num_topics, id2word = self.dictionary, passes = passes)
		print 'Done fitting LDA model.\n'

	def save(self, fileName):
		print 'Saving fitted LDAModel.\n'
		self.ldamodel.save(fileName + '.model')
		print 'Done saving LDAModel.\n'