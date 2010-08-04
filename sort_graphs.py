def sort_graphs(key):
	graphType = 0
	if triples[key].has_key('artAuthor'):  #It's the citing article graph
		graphType = '00-'
	elif triples[key].has_key('refAuthor'): #It's a cited article
		graphType = '01-'
	elif triples[key].has_key('authorMainName'): #It's an author graph
		graphType = '02-'
	else:
		print "Graph types unknown"
		graphType = '99-'
		
	sortKey = graphType + str(key)
	return sortKey