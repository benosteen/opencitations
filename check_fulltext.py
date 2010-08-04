from elementtree import ElementTree
from nlm_datamodel import get_datamodel

def check_fulltext (inputFile): 
	xmlRoot = ElementTree.parse(inputFile)
	datamodel = get_datamodel() 
	
	hasFulltext = 0
	if xmlRoot.find(datamodel['fulltextElement']) != None:
		hasFulltext = 1
	
	return hasFulltext