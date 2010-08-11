from elementtree import ElementTree

def check_fulltext (inputFile, datamodel): 
	xmlRoot = ElementTree.parse(inputFile)
	
	from MyConfigParser import MyConfigParser  #Uses my own modified version of ConfigParser, to facilitate character escaping
	#Get namespace authorities from separate manifest
	config = MyConfigParser()
	config.read('nlm_datamodel.cfg')
	#Read the config into a standard dictionary object (mostly just to avoid rewriting the existing code which reads the config from a dictionary)
	datamodel = {}
	for section in config.sections():
		datamodel[section] = {}
		for key in config.options(section):
			datamodel[section][key] = config.get(section, key)
	
	hasFulltext = 0
	if xmlRoot.find(datamodel['wrappers']['fulltextElement']) != None:
		hasFulltext = 1
	
	return hasFulltext