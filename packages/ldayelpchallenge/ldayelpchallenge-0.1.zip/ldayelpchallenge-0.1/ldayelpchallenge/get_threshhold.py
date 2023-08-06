def fivePercent(distances, percentage = 0.05):
	total = 0
	for value in distances.itervalues():
		total += value
	five = total * percentage
	tmp = 0
	fiver = 1
	dist = sorted([float(key) for key in distances.iterkeys()])
	for dst in dist:
		tmp += distances[dst]
		if(tmp >= five):
			fiver = dst
			break
	return fiver