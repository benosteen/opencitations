# Note on conventions:

# -  anything starting with doubled __underscore is yet to be decided what predicate should be used
# - things with no prefix, like fulltextElement, are not used as output predicated, but as steps in processing


def get_datamodel ():
	#This maps the information we need onto the NLM xml elements
	datamodel = {}
	datamodel['artWrapperElement'] = './/front'
	datamodel['fulltextElement'] = './/body'
	
	datamodel['artIdentifierElement'] = './/article-id[@pub-id-type="pmc"]'
	datamodel['artIdentifierBase'] = 'ukpmc.ac.uk/pmc-id/'
	
	datamodel['artMetadata'] = {
		#Various identifiers
		'__pubmedcentralId': './/article-id[@pub-id-type="pmc"]', #Note this is the same xml node used to create a URI for the article graph, at 'artIdentifierElement' above
		'__pubmedId': './/article-id[@pub-id-type="pmid"]',
		'__publishersId': './/article-id[@pub-id-type="publisher-id"]',
		
		'dc:title': './/article-title',
		'dc:creator': './/contrib[@contrib-type="author"]',
		
		#Journal details
		'__pubmedJournalAbbrev': './/journal-id[@journal-id-type="nlm-ta"]',
		'__journalTitle': './/journal-title',
		'__journalIssnPrint': './/issn[@pub-type="ppub"]',
		'__journalIssnElectronic': './/issn[@pub-type="epub"]',
		'__publisherName': './/publisher-name',
		
		'prism:volume': './/volume',
		'prism:issue': './/issue',
		'prism:startingPage': './/fpage',
		'prism:endingPage': './/lpage',
		
		#Date
		'__printPublicationYear': './/pub-date[@pub-type="ppub"]/year',
		'__ePublicationYear': './/pub-date[@pub-type="epub"]/year',
		
		#Copyright
		'__copyRightStatement': './/copyright-statement',
		'__licenseStatement': './/license'
	}
	
	datamodel['__licenseURL'] = '{http://www.w3.org/1999/xlink}href' # This is an attribute that has a namespace - note the syntax in which the namespace has to be provided, and that it must be the *real namespace*, not the prefix used to represent it inline
	
	datamodel['refElement'] = './/ref' #The wrapper for a single citation in the references list
	datamodel['refIdentifierElement'] = './/pub-id[@pub-id-type="pmid"]'
	datamodel['refIdentifierBase'] = 'ukpmc.ac.uk/pmid/'
	
	datamodel['refMetadata'] = {
		'dc:title': './/article-title',
		'dc:creator': './/name',
		'__journalTitle': './/source',
		'prism:startingPage': './/fpage',
		'prism:endingPage': './/lpage',
		'prism:volume': './/volume',
		'fabio:hasPublicationYear': './/year'
		#'': '',
	}
	
	datamodel['authorMetadata'] = {
		'foaf:firstName': './/given-names',
		'foaf:familyName': './/surname',
		'affiliationRef': ".//xref[@ref-type='aff']",
		'correspondenceRef': ".//xref[@ref-type='corresp']",
		'__qualifications': './/degrees'
	}
	
	datamodel['correspondence'] = './/corresp'
	datamodel['correspondenceIdentifier'] = 'id'
	datamodel['__email'] = './/email'
	
	datamodel['affiliationWrapper'] = './/aff'
	datamodel['affiliationIdentifier'] = 'id'
	datamodel['affiliation'] = {
		'foaf:name': './/institution',
		'v:adr': './/addr-line'
	}
	return datamodel
	
def get_namespaces ():
	namespaces ={}
	
	namespaces['xlink'] = 'http://www.w3.org/1999/xlink'
	
	return namespaces