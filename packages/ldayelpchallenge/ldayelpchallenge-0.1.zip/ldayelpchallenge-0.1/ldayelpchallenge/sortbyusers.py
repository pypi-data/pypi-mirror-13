def sortByUsers(tokDocs):
	userDocs = {}
	for value in tokDocs.itervalues():
		user = value['user']
		tokens = value['tokens']
		try:
			userDocs[user].append(tokens)
		except KeyError:
			userDocs[user] = []
			userDocs[user].append(tokens)
	return userDocs