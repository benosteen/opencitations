# # # # # # # #
# DEPRECATED! #
# # # # # # # #

import re

def get_vocabulary (input):
	vocabulary = {
		'entityType': 'rdf:type',
		'description': 'dc:description',
		
		# These are the controlled vocabulary terms for the "element names" used for reading from xml sources
		'artAuthor': 'terms:creator',
		'refAuthor': 'terms:creator',
		'authorGivenName': 'foaf:firstName',
		'authorMainName': 'foaf:familyName',
		'qualifications': '__qualifications',
		'affiliation': 'foaf:member',
		#'correspondence': '__correspondence',
		'email': '__email',
		
		'institution': 'foaf:name',
		'address': 'v:adr',
		
		#Various ids
		'pubmedcentralId': '__pubmedcentralId',
		'pubmedId': '__pubmedId',
		'publishersId': '__publishersId',
		
		'journalTitle': '__journalTitle',  # what to use here?
		'pubmedJournalAbbrev': '__pubmedJournalAbbrev',
		'journalIssnPrint': '__journalIssnPrint',
		'journalIssnElectronic': '__journalIssnElectronic',
		'publisherName': '__publisherName',
		
		'artVolume': 'prism:volume', 
		'artIssue': 'prism:issue',
		'artTitle': 'dc:title',
		
		'artPubYear': '__printPublicationYear', # Will later need to be restructured as frbr:embodiment	[[rdf:type	print-object; fabio:hasPublicationYear	"YYYY"], [rdf:type	digital-information-object; fabio:hasPublicationYear	"YYYY"]]
		'artEpubYear': '__ePublicationYear', # As with previous
		'artFirstPage': 'prism:startingPage', 
		'artLastPage': 'prism:endingPage',
		
		'copyRightStatement': '__copyRightStatement',
		'licenseStatement': '__licenseStatement',
		'licenseURL': '__licenseURL',
		
		'refJournal': 'bibtex:hasJournal', 
		'refVolume': 'prism:volume',
		'refFirstPage': 'prism:startingPage', 
		'refLastPage': 'prism:endingPage',
		'refTitle': 'dc:title',
		'refYear': 'fabio:hasPublicationYear',
		'references': 'cito:cites',
		
		# These are the controlled vocabulary terms for the predicates used in PLoS triples data
		'dcterms:references': 'cito:cites',
		'rdf:type': 'rdf:type',
		'topaz:ELocationId': 'topaz:ELocationId',
		'prism:volume': 'prism:volume',
		'plos:hasAuthorList': 'plos:hasAuthorList',
		'plos:hasEditorList': 'plos:hasEditorList',
		'plos-temporal:displayYear': 'fabio:hasPublicationYear',
		'bibtex:hasYear': 'fabio:hasPublicationYear',
		'bibtex:hasVolume': 'prism:volume',
		'bibtex:hasPages': 'bibtex:hasPages',
		'bibtex:hasKey': 'bibtex:hasKey',
		'bibtex:hasJournal': 'bibtex:hasJournal',
		'bibtex:hasAddress': 'v:adr',
		'bibtex:hasPublisher': 'bibtex:hasPublisher',
		'': '',
		'': '',
		'': ''
	}
	
	output = 0
	if vocabulary.has_key(input):
		output = vocabulary[input]
	elif re.search('rdf:_\d+', input):
		output = input
	else:
		print "Couldn't find the output vocab for " + str(input)
	
	return output