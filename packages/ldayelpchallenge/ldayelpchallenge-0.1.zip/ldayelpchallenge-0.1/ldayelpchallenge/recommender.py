import json
import numpy as np

class Recommender():

	def __init__(self, means):
		self.means = means

	def findClosest(self, userID, distanceMeasure):		
		toCheck = self.means[userID]
		closest = [float('inf'), None]
		for key, value in self.means.iteritems():
			if key != userID:
				x = distanceMeasure(np.array(toCheck), np.array(value))				
				if  x < closest[0]:
					closest[0] = x
					closest[1] = key
		return closest

	def calc_neighbors(self, userID, distanceMeasure, threshhold = None):
		toCheck = self.means[userID]
		neighbors = []
		for key, value in self.means.iteritems():
			if key != userID:
				x = distanceMeasure(np.array(toCheck), np.array(value))
				if(threshhold):
					if(round(x,2) <= threshhold):
						neighbors.append([x, key])
				else:
					neighbors.append([x, key])
		return neighbors

	def calc_distances(self, distanceMeasure):
		distances = {}
		for user in self.means.iterkeys():
			for key, value in self.means.iteritems():
				if key != user:
					x = round(distanceMeasure(np.array(self.means[user]), np.array(value)), 2)
					if x in distances:
						distances[x] += 1
					else:
						distances[x] = 1
		return distances