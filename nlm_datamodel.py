def get_datamodel ():
	#This maps the information we need onto the NLM xml elements
	datamodel = {}
	datamodel['artWrapperElement'] = './/front'
	datamodel['fulltextElement'] = './/body'
	
	datamodel['artIdentifierElement'] = './/article-id[@pub-id-type="pmc"]'
	datamodel['artIdentifierBase'] = 'ukpmc.ac.uk/pmc-id/'
	
	datamodel['artMetadata'] = {
		#Various identifiers
		'pubmedcentralId': './/article-id[@pub-id-type="pmc"]', #Note this is the same xml node used to create a URI for the article graph, at 'artIdentifierElement' above
		'pubmedId': './/article-id[@pub-id-type="pmid"]',
		'publishersId': './/article-id[@pub-id-type="publisher-id"]',
		
		'artTitle': './/article-title',
		'artAuthor': './/contrib[@contrib-type="author"]',
		
		#Journal details
		'pubmedJournalAbbrev': './/journal-id[@journal-id-type="nlm-ta"]',
		'journalTitle': './/journal-title',
		'journalIssnPrint': './/issn[@pub-type="ppub"]',
		'journalIssnElectronic': './/issn[@pub-type="epub"]',
		'publisherName': './/publisher-name',
		
		'artVolume': './/volume',
		'artIssue': './/issue',
		'artFirstPage': './/fpage',
		'artLastPage': './/lpage',
		
		#Date
		'artPubYear': './/pub-date[@pub-type="ppub"]/year',
		'artEpubYear': './/pub-date[@pub-type="epub"]/year',
		
		#Copyright
		'copyRightStatement': './/copyright-statement',
		'licenseStatement': './/license'
	}
	
	datamodel['licenseURL'] = '{http://www.w3.org/1999/xlink}href' # This is an attribute that has a namespace - note the syntax in which the namespace has to be provided, and that it must be the *real namespace*, not the prefix used to represent it inline
	
	datamodel['refElement'] = './/ref' #The wrapper for a single citation in the references list
	datamodel['refIdentifierElement'] = './/pub-id[@pub-id-type="pmid"]'
	datamodel['refIdentifierBase'] = 'ukpmc.ac.uk/pmid/'
	
	datamodel['refMetadata'] = {
		'refTitle': './/article-title',
		'refAuthor': './/name',
		'refJournal': './/source',
		'refFirstPage': './/fpage',
		'refLastPage': './/lpage',
		'refVolume': './/volume',
		'refYear': './/year'
		#'': '',
	}
	
	datamodel['authorMetadata'] = {
		'authorGivenName': './/given-names',
		'authorMainName': './/surname',
		'affiliationRef': ".//xref[@ref-type='aff']",
		'correspondenceRef': ".//xref[@ref-type='corresp']",
		'qualifications': './/degrees'
	}
	
	datamodel['correspondence'] = './/corresp'
	datamodel['correspondenceIdentifier'] = 'id'
	datamodel['email'] = './/email'
	
	datamodel['affiliationWrapper'] = './/aff'
	datamodel['affiliationIdentifier'] = 'id'
	datamodel['affiliation'] = {
		'institution': './/institution',
		'address': './/addr-line'
	}
	return datamodel
	
def get_namespaces ():
	namespaces ={}
	
	namespaces['xlink'] = 'http://www.w3.org/1999/xlink'
	
	return namespaces