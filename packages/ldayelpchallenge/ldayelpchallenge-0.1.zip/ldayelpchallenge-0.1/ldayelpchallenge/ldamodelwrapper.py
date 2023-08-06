from gensim import corpora, models
import os
import json

class LDAModelWrapper:
	"""Wrapper for loading and interacting with a precalculated LDAModel"""

	def __init__(self, LdaModel, dictionary, userTokens):
		if type(LdaModel) == str:
			self.ldamodel = models.LdaModel.load(LdaModel)	
		else:
			self.ldamodel = LdaModel
		if type(dictionary) == str:
			with open(dictionary) as f:
				self.dictionary = json.loads(f.read())
		else:
			self.dictionary = dictionary
		self.userTokens = userTokens

	def get_user_posteriors(self, userTokens):
		posteriors = []
		for tokens in userTokens:
			bow = self.dictionary.doc2bow(tokens)
			posteriors.append(self.ldamodel.get_document_topics(bow))
		return posteriors

	def get_all_posteriors(self):
		posteriors = {}
		for user, tokens in self.userTokens.iteritems():						
			posteriors[user] = self.get_user_posteriors(tokens)		
		return posteriors