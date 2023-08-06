from LDAsetup import *
import json
from filter_lang import filter_by_language
import sys
from math_helper import *
from ldamodelwrapper import LDAModelWrapper
from sortbyusers import sortByUsers
from get_threshhold import fivePercent
from recommender import Recommender

def run(source, target, num_topics = 100, passes = 20, lang = 'en', distance_measure = euclidean, percentage = 0.05):
	with open(source) as f:
		all_reviews = []
		for line in f:
			all_reviews.append(json.loads(line))

	reviews = filter_by_language(all_reviews, lang)

	rt = ReviewTokenizer(reviews)
	rt.tokenize()

	db = DictionaryBuilder(rt.tokenized_docs)
	db.build()

	dtmb = DTMBuilder(db.dictionary, db.srcTexts)
	dtmb.build()

	ldaw = LDAWrapper(dtmb.dtm, db.dictionary)
	ldaw.run(num_topics = num_topics, passes = passes)

	modelwrapper = LDAModelWrapper(ldaw.ldamodel, db.dictionary, sortByUsers(rt.tokenized_docs))
	posteriors = modelwrapper.get_all_posteriors()

	means = {}
	for key, value in posteriors.iteritems():
		means[key] = mean(value).tolist()

	x = Recommender(means)
	y = x.calc_distances(distance_measure)

	threshhold = fivePercent(y, percentage)

	for user in means.iterkeys():
		z = x.calc_neighbors(user, distance_measure, threshhold = threshhold)
		if len(target) > 0:
			fileName = target + '/' + user + '.json'
		else:
			fileName = user + '.json'
		with open(fileName, 'w') as g:
			json.dump(z, g) 