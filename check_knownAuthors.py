import re
from elementtree import ElementTree

def check_knownAuthors (authorData, triples):

	#Switch this module off;
	return None

	#No fuzziness implemented. Just checks all the fields to see if they all match up against some existing record
	knownAuthor = None
	
	if len(authorData.keys()) == 0:
		return None
	
	existingAuthors = {} # Clone the triples dictionary
	for item in triples.keys():
		if triples[item].has_key('authorMainName'):
			existingAuthors[item] = triples[item]
	
	for metaField in authorData.keys():
		value = authorData[metaField]
		
		#Go through the collection of known entities, throwing away anything that doesn't match this value
		for entity in existingAuthors.keys():
			# First check if the entity even has this field, and if not skip it
			if not existingAuthors[entity].has_key(metaField):
				continue
			
			if type(value).__name__=='dict':
				for key in existingAuthors[entity][metaField].keys():
					if not existingAuthors[entity][metaField][key] == value[key]:
						del existingAuthors[entity] #throw it away
			elif not existingAuthors[entity][metaField] == value:
				del existingAuthors[entity] #throw it away
	
	#whatever is left must have all the same param values - i.e. it's a match
	for entity in existingAuthors.keys():
		knownAuthor = entity
		print "For this author: "
		print authorData
		print "I found a matching author: "
		for key in existingAuthors[knownAuthor].keys():
			print str(key) + ": " + str(existingAuthors[knownAuthor][key])
	
	return knownAuthor