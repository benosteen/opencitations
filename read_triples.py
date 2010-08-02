"""
read_triples.py 
"""

import re
import sys
from rdf_string_cleanup import predicate_cleanup
from rdf_string_cleanup import value_cleanup
from nlm_datamodel import get_datamodel
from hashlib import md5
from check_knownAuthors import check_knownAuthors
from elementtree import ElementTree

# Method for reading in from n-triples format
def read_nTriples (inputFile, authorities):
	triples = {}
	
	for line in inputFile:
		line = line.rstrip() #this is Python's chomp function
	
		fields = re.split('\s+', line)
		
		subject = predicate = values = None
		
		if ( ( len(fields)==3 ) and ( re.search('^<.+>$', fields[0]) or re.search('^<.+>$', fields[1]) ) ):
		
			subject = fields[0]
			predicate = fields[1]
			#value = fields[2]
			values = fields[2].split(", ")
			
		else:
			#This doesn't seem to be a triple. Skip to next line
			subject = predicate = values = None
			continue
		
		#Send these variables off for cleanup
		predicate = predicate_cleanup(predicate, authorities)
		values = value_cleanup(values)
		
		#Python but not Perl: If there is not yet a second-level dictionary object for this subject, need to create it. (Otherwise the attempt below to look up a predicate key under this subject will cause an error.)
		if not triples.has_key(subject):
			triples[subject] = {} 
		
		#Add this to hash entry, or create a new hash entry if required
		if triples[subject].has_key(predicate):
			triples[subject][predicate] = triples[subject][predicate] + values
			#triples[subject][predicate].append(values)
		else:
			triples[subject][predicate] = values
			
	return triples

def make_matchString (elementName):
	matchString = '<'+str(elementName)+'( [^>]+)?>(.+?)</'+str(re.sub(' .+$', '', elementName))+'>'
	return matchString

# A utility for scraping xml element content, as used in read_xml() below
def get_elementContent (sourceString, elementName, inputFile):
	matchString = make_matchString(elementName)
	
	results = []
	if re.search(matchString, str(sourceString), re.IGNORECASE | re.DOTALL): 
		matches = re.findall(matchString, str(sourceString), re.IGNORECASE | re.DOTALL)
		#matches is now a list of matchgroups. from each matchgroup we want the second group (unless it's empty)
		
		for matchGroup in matches:
			if matchGroup[1]=='': #Filter to substantive results only
				continue
			else:
				results.append(matchGroup[1])
			
	else:
		print "Couldn't find <" + str(elementName) + "> content in file " + str(inputFile.name)
		#print matchString
		#print str(sourceString)
		
	return results

#Helper function I had to write, because ElementTree's text parser is really bad!
def get_text (xmlElement):
	xmlElement.tail = None #Get rid of "tail" text
	textString = ElementTree.tostring(xmlElement) #Get the whole element as a string
	textString = re.sub('<[^>]+>', '', textString) #Remove tags
	return textString

# Method for reading in from xml format
def read_xml (inputFile, authorities):
	
	triples = {}
	
	# Read the input as a single string
	inputString = inputFile.read()
	
	# Need to use the string to get the DOCTYPE, before parsing it into an xml tree
	doctype = 0
	matches = re.findall('<!DOCTYPE[^>]+>', inputString, re.IGNORECASE)
	if not len(matches)==1: #We want one doctype, and one only
		sys.exit("XML input has no doctype, or multiple doctypes")
	else:
		doctype = matches[0]
		
	# Is it NLM markup? ... For the moment this is the only datamodel we will accept
	if not re.search('nlm', doctype, re.IGNORECASE):
		sys.exit("XML input has some DTD that is not NLM. Will need to extend the code to deal with a range of DTDs.")
	
	xmlRoot = ElementTree.fromstring(inputString) 
	
	#print xmlRoot
	""" START ElementTree TESTING
	ids = xmlRoot.findall('.//article-id[@pub-id-type="pmid"]')
	for id in ids:
		tag = id.tag
		text = id.text
		attribute = id.get('pub-id-type')
		element = ElementTree.tostring(id)
		
		print "TAG: " + tag
		print "TEXT: " + text
		print "ATT: " + attribute
		print "ELEMENT: " + element
	END ElementTree TESTING """
	
	datamodel = get_datamodel() # Imports the (NLM) datamodel as a multidimensional dictionary object
	
	#Get the block of article information, using the datamodel to navigate the xml
	artWrapper = xmlRoot.find(datamodel['artWrapperElement'])
	
	#From the artWrapper, get the unique article identifier
	artIdentifier = artWrapper.find(datamodel['artIdentifierElement'])
	artIdentifier = "<"+str(datamodel['artIdentifierBase'])+get_text(artIdentifier)+">" #This has to be a single string, with carats to mark it as a unique identifier
	
	triples[artIdentifier] = {} # Create a dictionary entry for the article
	
	# START affiliations bit needed for NLM xml. It's kindof awkward, but I can't think of any more elegant way of doing it.
	affiliationData = {}
	#affiliations = get_elementContent(artWrapper, datamodel['affiliationWrapper'], inputFile)
	affiliations = artWrapper.findall(datamodel['affiliationWrapper'])
	affiliations = list(result for result in affiliations) #turn it into a list
	
	if len(affiliations) >= 1: #As long as the affiliations aren't empty...
	
		#If the affiliations are listed with identifiers, then there will be multiple affiliations. Analyse them separately, so that authors can be linked to them separately
		if affiliations[0].find(datamodel['affiliationIdentifier']) != None:
			for aff in affiliations:
				#affiliationId = get_elementContent(aff, datamodel['affiliationIdentifier'], inputFile)
				affiliationId = aff.find(datamodel['affiliationIdentifier'])
				affiliationId = value_cleanup(get_text(affiliationId)) #get string
				affiliationData[affiliationId] = {}
				for elementName in datamodel['affiliation'].keys():
					#data = get_elementContent(aff, datamodel['affiliation'][elementName], inputFile)
					data = aff.find(datamodel['affiliation'][elementName])
					if data != None:
						data = value_cleanup(get_text(data))
						affiliationData[affiliationId][elementName] = data
				#Sometimes the affiliation data is unstructured, so:
				if affiliationData[affiliationId].keys()==None:
					affiliationData[affiliationId]['dc:Description'] = get_text(aff)
				affiliationData[affiliationId]['rdf:type'] = ['foaf:Organization']
		# Otherwise, just describe one affiliation (and give it a 'dummyRef'
		else:
			aff = 0
			if len(affiliations) > 1:
				print "Multiple affiliations, but no xrefs to attach authors to affiliations"
			
			aff = affiliations[0]
				
			affiliationId = 'dummyRef'
			affiliationData[affiliationId] = {}
			for elementName in datamodel['affiliation'].keys():
				data = aff.find(datamodel['affiliation'][elementName])
				if data != None:
					data = value_cleanup(get_text(data))
					affiliationData[affiliationId][elementName] = data
			#Sometimes the affiliation data is unstructured, so:
			if len(affiliationData[affiliationId].keys()) == 0:
				affiliationData[affiliationId]['description'] = get_text(aff)
			affiliationData[affiliationId]['rdf:type'] = ['foaf:Organization']
	# END affiliation bit 
	
	
	#And now get each of the article metadata fields from the artWrapper; when you get to authors, given them their own graphs
	for elementName in datamodel['artMetadata'].keys():
		data = artWrapper.findall(datamodel['artMetadata'][elementName])
		data = list(result for result in data) #turn it into a list
		if elementName=='artAuthor':
			#Create a graph for each article author, then use the URI of that graph as the identifier in the article graph
			authorURIs = []
			for eachAuthor in data:
				
				#Collect the author metadata, and use it to see whether this author is new, or already known
				authorData = {}
				for metaField in datamodel['authorMetadata'].keys():
					data = eachAuthor.findall(datamodel['authorMetadata'][metaField])
					data = list(get_text(result) for result in data) #turn it into a list
					data = value_cleanup(data)
					
					if data != []:
						authorData[metaField] = data
				
				#If the author has a ref to one of multiple affiliations listed
				if authorData.has_key('affiliationRef'):
					# Replace the affiliationRef field with an affiliation field
					affiliationRef = authorData['affiliationRef']
					affiliationRef = affiliationRef[0]
					affiliation = affiliationData[affiliationRef]
					authorData['affiliation'] = affiliation
					del authorData['affiliationRef']
				#Otherwise just link it to the one only affiliation
				elif affiliationData.has_key('dummyRef'):
					authorData['affiliation'] = affiliationData['dummyRef']
				
				knownAuthor = check_knownAuthors(authorData, triples)
				
				if not knownAuthor==None: #Already seen this author before
					authorURIs.append(knownAuthor)
					
				else: #New author, create a URI and a graph in triples
					authorId = md5() #Create an md5 hash object
					authorId.update(get_text(eachAuthor))
					authorId = "<"+str(authorId.hexdigest())+">"
					authorURIs.append(authorId)
					triples[authorId] = {}
					for metaField in authorData.keys():
						content = authorData[metaField]
						triples[authorId][metaField] = content
			
			authorURIs = value_cleanup(authorURIs)
			triples[artIdentifier][elementName] = authorURIs
		
		#It's not the author data
		else:
			data = list(get_text(result) for result in data) # make it a list of strings
			data = value_cleanup(data)
			triples[artIdentifier][elementName] = data
	
	#Make a graph for each cited work in the references section
	refList = xmlRoot.findall(datamodel['refElement'])
	refList = list(result for result in refList) #turn it into a list

	refIDs = []
	for ref in refList:
		refIdentifier = ref.find(datamodel['refIdentifierElement'])
		#If there was no identifier, we will have to make a hash
		if refIdentifier == None:
			refIdentifier = md5() #Create an md5 hash object
			refIdentifier.update(get_text(ref))
			refIdentifier = "<"+str(refIdentifier.hexdigest())+">"
			#print "REFID: " + refIdentifier
		else:
			refIdentifier = "<"+str(datamodel['refIdentifierBase'])+get_text(refIdentifier)+">" #This has to be a single string, with carats to mark it as a unique identifier

		triples[refIdentifier] = {} # Create a dictionary entry for the ref
		
		#And now get each of the reference metadata fields from the ref
		for elementName in datamodel['refMetadata'].keys():
			data = ref.findall(datamodel['refMetadata'][elementName])
			data = list(result for result in data) #turn it into a list 
			#print data
			
			if elementName=='refAuthor':
				#Create a graph for each article author, then use the URI of that graph as the identifier in the article graph
				authorURIs = []
				for eachAuthor in data:
					
					#Collect the author metadata, and use it to see whether this author is new, or already known
					authorData = {}
					for metaField in datamodel['authorMetadata'].keys():
						# No affiliation data for ref authors
						if metaField=='affiliationRef':
							continue
						data = eachAuthor.findall(datamodel['authorMetadata'][metaField])
						data = list(get_text(result) for result in data) #turn it into a list
						data = value_cleanup(data)
						
						if data != []:
							authorData[metaField] = data
					
					knownAuthor = check_knownAuthors(authorData, triples)
					
					if not knownAuthor==None: #Already seen this author before
						authorURIs.append(knownAuthor)
						
					else: #New author, create a URI and a graph in triples
						authorId = md5() #Create an md5 hash object
						authorId.update(get_text(eachAuthor))
						authorId = "<"+str(authorId.hexdigest())+">"
						#print "AUTHID: " + authorId
						authorURIs.append(authorId)
						triples[authorId] = {}
						for metaField in authorData.keys():
							content = authorData[metaField]
							content = value_cleanup(content)
							triples[authorId][metaField] = content
				
				authorURIs = value_cleanup(authorURIs)
				triples[refIdentifier][elementName] = authorURIs
			else:
				data = list(get_text(result) for result in data) # make it a list of strings
				data = value_cleanup(data)
				triples[refIdentifier][elementName] = data
		
		refIDs.append(refIdentifier)
	
	#And for each reference add a triple to the article graph
	refIDs = value_cleanup(refIDs)
	triples[artIdentifier]['references'] = refIDs
	
	return triples

#Method for receiving input, sending to correct reader according to format
def read_triples(inputFile, inputFormat, authorities):
	triples = {}
	
	if re.search('triple', inputFormat, re.IGNORECASE):
		triples = read_nTriples(inputFile, authorities)
	
	elif re.search('xml', inputFormat, re.IGNORECASE):
		triples = read_xml(inputFile, authorities)
		
	return triples