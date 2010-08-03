def get_datamodel ():
	#This maps the information we need onto the NLM xml elements
	datamodel = {}
	datamodel['artWrapperElement'] = './/front'
	datamodel['artIdentifierElement'] = './/article-id[@pub-id-type="pmc"]'
	datamodel['artIdentifierBase'] = 'ukpmc.ac.uk/pmid/'
	datamodel['artMetadata'] = {
		'artTitle': './/article-title',
		'artAuthor': './/contrib[@contrib-type="author"]',
		'artJournal': './/journal-id[@journal-id-type="nlm-ta"]',
		'artVolume': './/volume',
		'artFirstPage': './/fpage',
		'artLastPage': './/lpage',
		'artYear': './/year'
	}
	
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
		'affiliationRef': ".//xref[@ref-type='aff']"
	}
	
	datamodel['affiliationWrapper'] = './/aff'
	datamodel['affiliationIdentifier'] = 'id'
	datamodel['affiliation'] = {
		'institution': './/institution',
		'address': './/addr-line'
	}
	return datamodel