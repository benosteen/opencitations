"""
read_triples.py 
"""

import re
import sys
from rdf_string_cleanup import predicate_cleanup
from rdf_string_cleanup import value_cleanup
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
			values = fields[2].split(", ")
			
		else:
			#This doesn't seem to be a triple. Skip to next line
			subject = predicate = values = None
			continue
		
		#Send these variables off for cleanup
		predicate = predicate_cleanup(predicate, authorities)
		values = value_cleanup(values, authorities)
		
		#Python but not Perl: If there is not yet a second-level dictionary object for this subject, need to create it. (Otherwise the attempt below to look up a predicate key under this subject will cause an error.)
		if not triples.has_key(subject):
			triples[subject] = {} 
		
		#Add this to hash entry, or create a new hash entry if required
		if triples[subject].has_key(predicate):
			triples[subject][predicate] = triples[subject][predicate] + values
			#triples[subject][predicate].append(values)
		else:
			triples[subject][predicate] = values
	
	# Make sure all the graphs have an rdf:type
	for subject in triples.keys():
		if not triples[subject].has_key('rdf:type'):
			if triples[subject].has_key('plos:hasAuthorList') or triples[subject].has_key('dc:creator') or triples[subject].has_key('cito:cites') or triples[subject].has_key('dcterms:references'): #So it's an article
				triples[subject]['rdf:type'] = 'fabio:Document'
			elif triples[subject].has_key('foaf:familyName'): #So it's an author
				triples[subject]['rdf:type'] = 'fabio:Person'
			else:
				print "Graph for %s lacks rdf:type" % subject
	
	return triples


#Helper function I had to write, because ElementTree's text parser is really bad!
def get_text (xmlElement):
	xmlElement.tail = None #Get rid of "tail" text
	textString = ElementTree.tostring(xmlElement) #Get the whole element as a string
	textString = re.sub('<[^>]+>', '', textString) #Remove tags
	return textString
	

# For extracting author affiliations; decided to make this a separate function (compared to other content extraction) because it's rather complicated
def get_affiliations (artWrapper, datamodel):
	affiliationData = {}
	affiliations = artWrapper.findall(datamodel['wrappers']['affiliationWrapper'])
	affiliations = list(result for result in affiliations) #turn it into a list
	
	#If there are multiple affiliations, then analyse them separately so that authors can be linked to them separately
	if len(affiliations) > 1:
		for aff in affiliations:
			affiliationId = aff.attrib.get(datamodel['identifiers']['affiliationIdentifier'])
			if affiliationId == None:
				print "Multiple affiliations, but at least one of the affiliations lacks an ID that allows it to be associated with particular authors"
				continue
			affiliationId = value_cleanup(affiliationId)
			
			affiliationData[affiliationId] = {}
			for elementName in datamodel['affiliation'].keys():
				data = aff.findall(datamodel['affiliation'][elementName])
				data = list(get_text(result) for result in data) # listify
				if data:
					data = value_cleanup(data)
					affiliationData[affiliationId][elementName] = data
			#Sometimes the affiliation data is unstructured, so:
			if affiliationData[affiliationId].keys() == []:
				
				#Need to remove label and sup elements
				textString = ElementTree.tostring(aff)
				textString = re.sub('<label( [^>]+)?>.+?</label>', '', textString)
				textString = re.sub('<sup( [^>]+)?>.+?</sup>', '', textString)
				aff = ElementTree.fromstring(textString)
				
				affiliationData[affiliationId]['dc:description'] = get_text(aff)
			affiliationData[affiliationId]['rdf:type'] = ['foaf:Organization']
	
	# Otherwise, just describe one affiliation (and give it a 'dummyRef'
	elif len(affiliations) == 1:
		aff = affiliations[0]
		# Sometimes there will still be an identifier, even on a single affiliation
		affiliationId = 0
		if aff.attrib.get(datamodel['identifiers']['affiliationIdentifier']):
			affiliationId = aff.attrib.get(datamodel['identifiers']['affiliationIdentifier'])
			affiliationId = value_cleanup(affiliationId)
		else: #otherwise use this pseudo-identifier
			affiliationId = 'dummyRef'
			
		affiliationData[affiliationId] = {}
		for elementName in datamodel['affiliation'].keys():
			data = aff.find(datamodel['affiliation'][elementName])
			if data:
				data = value_cleanup(get_text(data))
				affiliationData[affiliationId][elementName] = data
		
		#Sometimes the affiliation data is unstructured, so:
		if affiliationData[affiliationId].keys() == []:
			
			#Need to remove label and sup elements
			textString = ElementTree.tostring(aff)
			textString = re.sub('<label( [^>]+)?>.+?</label>', '', textString)
			textString = re.sub('<sup( [^>]+)?>.+?</sup>', '', textString)
			aff = ElementTree.fromstring(textString)
				
			affiliationData[affiliationId]['dc:description'] = get_text(aff)
		
		affiliationData[affiliationId]['rdf:type'] = ['foaf:Organization']
	
	
	# Also check for email addresses that are linked to certain authors. Will only record email addresses, and not any other correspondence text.
	correspondences = artWrapper.findall(datamodel['correspondence']['correspondence'])
	correspondences = list(result for result in correspondences) #turn it into a list
	
	for corres in correspondences:
		if corres.attrib.get(datamodel['correspondence']['correspondenceIdentifier']):
			corresId = corres.attrib.get(datamodel['correspondence']['correspondenceIdentifier'])
			corresId = value_cleanup(corresId)
			
			if corres.find(datamodel['correspondence']['v:email']): # If there is an email address, get that
				email = corres.find(datamodel['correspondence']['v:email'])
				affiliationData[corresId] = {'v:email': value_cleanup(get_text(email))}
			else: # Otherwise get whatever kind of unstructured contact details are available
				affiliationData[corresId] = {'v:adr': value_cleanup(get_text(corres))}
	
	return affiliationData

def add_author_data (triples, data, datamodel, affiliationData, artIdentifier):
#Create a graph for each article author, then use the URI of that graph as the identifier in the article graph
	authorURIs = []
	for eachAuthor in data:
		
		#Collect the author metadata, and use it to see whether this author is new, or already known
		authorData = {}
		for metaField in datamodel['authorMetadata'].keys():
			data = 0
			if metaField != 'affiliationRef' and metaField != 'correspondenceRef':
				data = eachAuthor.findall(datamodel['authorMetadata'][metaField])
				data = list(get_text(result) for result in data) #turn it into a list
			elif metaField == 'affiliationRef' or metaField == 'correspondenceRef':
				element = eachAuthor.find(datamodel['authorMetadata'][metaField])
				if not element:
					continue
				data = element.attrib.get('rid') #Need to do this extra step - only way ElementTree allows you to get an attribute from a descendant element (not directly supported in their "find" xpath function
			data = value_cleanup(data)
			
			if data:
				authorData[metaField] = data
		
		if affiliationData:
			#If the author has a ref to one of multiple affiliations listed, record that as their affiliation
			if authorData.has_key('affiliationRef'):
				# Replace the affiliationRef field with an affiliation field
				affiliationRef = authorData['affiliationRef']
				affiliation = affiliationData[affiliationRef]
				authorData['affiliation'] = affiliation
				del authorData['affiliationRef']
			#Otherwise just link it to the one only affiliation
			elif affiliationData.has_key('dummyRef'):
				authorData['affiliation'] = affiliationData['dummyRef']
			
			if authorData.has_key('correspondenceRef'):
				# Replace the affiliationRef field with an affiliation field
				correspondenceRef = authorData['correspondenceRef'] 
				if affiliationData.has_key(correspondenceRef):
					correspondence = affiliationData[correspondenceRef]
					authorData['v:vcard'] = correspondence
				else:
					print "Author correspondence ref %s could not be resolved to correspondence details." % correspondenceRef
				del authorData['correspondenceRef']
		
		knownAuthor = check_knownAuthors(authorData, triples)
		
		if knownAuthor: #Already seen this author before
			authorURIs.append(knownAuthor)
			
		else: #New author, create a URI and a graph in triples
			authorId = md5() #Create an md5 hash object
			authorId.update(get_text(eachAuthor))
			authorId = "<"+str(authorId.hexdigest())+">"
			authorURIs.append(authorId)
			triples[authorId] = {}
			triples[authorId]['rdf:type'] = 'foaf:Person'
			for metaField in authorData.keys():
				content = authorData[metaField]
				triples[authorId][metaField] = content
	
	authorURIs = value_cleanup(authorURIs)
	triples[artIdentifier]['dc:creator'] = authorURIs
	
	return triples

# Method for reading in from xml format
def read_xml (inputFile, authorities):
	triples = {}
	hasFulltext = 0
	
	# Read the input as a single string
	inputString = inputFile.read()
	
	# Need to use the string to get the DOCTYPE, before parsing it into an xml tree
	doctype = 0
	matches = re.findall('<!DOCTYPE[^>]+>', inputString, re.IGNORECASE)
	if not len(matches)==1: #We want one doctype, and one only
		#sys.exit("XML input has no doctype, or multiple doctypes")
		print "XML input has no doctype, or multiple doctypes"
		return triples
	else:
		doctype = matches[0]
		
	# Is it NLM markup? ... For the moment this is the only datamodel we will accept
	if not re.search('nlm', doctype, re.IGNORECASE):
		#sys.exit("XML input has some DTD that is not NLM. Will need to extend the code to deal with a range of DTDs.")
		print "XML input has some DTD that is not NLM. Will need to extend the code to deal with a range of DTDs."
		return triples
	
	xmlRoot = ElementTree.fromstring(inputString) 
	
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
	
	#Register the datamodel's xml namespaces with ElementTree
	for k, v in datamodel['xmlNamespaces'].items():
		ElementTree.register_namespace(k, v)
	
	#Check whether there is fulltext present (used for reporting only)
	if xmlRoot.find(datamodel['wrappers']['fulltextElement']):
		hasFulltext = 1
	
	#Get the block of article metadata info, using the datamodel to navigate the xml
	artWrapper = xmlRoot.find(datamodel['wrappers']['artWrapperElement'])
	
	#From the artWrapper, get the unique article identifier
	artIdentifier = artWrapper.find(datamodel['identifiers']['artIdentifierElement'])
	if artIdentifier == None:
		print "Couldn't get article identifier"
	artIdentifier = "<"+str(datamodel['identifiers']['artIdentifierBase'])+get_text(artIdentifier)+">" #This has to be a single string, with carats to mark it as a unique identifier
	
	triples[artIdentifier] = {} # Create a dictionary object for the article
	triples[artIdentifier]['rdf:type'] = 'fabio:Document' # It may be something more specific, but we don't know that yet
	
	# Before going on to collect other article metadata, collect the author affiliations data, which will be used in building graphs for the article authors
	affiliationData = get_affiliations(artWrapper, datamodel)
	
	#And now get each of the article metadata fields from the artWrapper; when you get to authors, given them their own graphs
	for elementName in datamodel['artMetadata'].keys():
		data = artWrapper.findall(datamodel['artMetadata'][elementName])
		data = list(result for result in data) #turn it into a list
		
		#Special treatment for author metadata
		if elementName=='dc:creator':
			triples = add_author_data(triples, data, datamodel, affiliationData, artIdentifier)
		
		#It's other standard metadata
		else:
			data = list(get_text(result) for result in data) # make it a list of strings
			if data != []:
				data = value_cleanup(data)
				triples[artIdentifier][elementName] = data
	
	#Some special treatment of the license info, to extract a link to the license URL if there is one
	if triples[artIdentifier].has_key('__licenseStatement'):
		license = artWrapper.find(datamodel['artMetadata']['__licenseStatement'])
		licenseURL = license.attrib.get(datamodel['identifiers']['__licenseURL'])
		if licenseURL != None:
			licenseURL = value_cleanup(licenseURL)
			triples[artIdentifier]['__licenseURL'] = licenseURL
	
	#Make a graph for each cited work in the references section
	refList = xmlRoot.findall(datamodel['wrappers']['refElement'])
	refList = list(result for result in refList) #turn it into a list

	refIDs = []
	for ref in refList:
		refIdentifier = ref.find(datamodel['identifiers']['refIdentifierElement'])
		#If there was no identifier, we will have to make a hash
		if refIdentifier == None:
			refIdentifier = md5() #Create an md5 hash object
			refIdentifier.update(get_text(ref))
			refIdentifier = "<"+str(refIdentifier.hexdigest())+">"
		else:
			refIdentifier = "<"+str(datamodel['identifiers']['refIdentifierBase'])+get_text(refIdentifier)+">" #This has to be a single string, with carats to mark it as a unique identifier  # No URI "base" for these yet - perhaps could add one?

		triples[refIdentifier] = {} # Create a dictionary entry for the ref
		triples[refIdentifier]['rdf:type'] = 'fabio:Document'
		
		#And now get each of the reference metadata fields from the ref
		for elementName in datamodel['refMetadata'].keys():
			data = ref.findall(datamodel['refMetadata'][elementName])
			data = list(result for result in data) #turn it into a list 
			#print data
			
			if elementName=='dc:creator':
				triples = add_author_data(triples, data, datamodel, None, refIdentifier)
			
			else:
				data = list(get_text(result) for result in data) # make it a list of strings
				if data != []:
					data = value_cleanup(data)
					triples[refIdentifier][elementName] = data
		
		refIDs.append(refIdentifier)
	
	#And for each reference add a triple to the article graph
	refIDs = value_cleanup(refIDs)
	if refIDs != []:
		triples[artIdentifier]['cito:cites'] = refIDs
	
	return triples, hasFulltext

#Method for receiving input, sending to correct reader according to format
def read_triples(inputFile, inputFormat, authorities):
	triples = {}
	hasFulltext = 0
	
	if re.search('triple', inputFormat, re.IGNORECASE):
		triples = read_nTriples(inputFile, authorities)
		hasFulltext = 0
	
	elif re.search('xml', inputFormat, re.IGNORECASE):
		(triples, hasFulltext) = read_xml(inputFile, authorities)
		
	return triples, hasFulltext