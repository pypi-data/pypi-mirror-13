import numpy as np

def mean(posteriors):
	container = [[0]*100]*len(posteriors)
	for index, posterior in enumerate(posteriors):
		for probability in posterior:
			topic = probability[0]
			prob = probability[1]
			container[index][topic] = prob
	a = np.array(container)
	return a.mean(axis=0)

def euclidean(x,y):   
    return np.sqrt(np.sum((x-y)**2))