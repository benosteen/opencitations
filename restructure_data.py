def restructure_data (inputGraph, inputFields):
	#print inputGraph
	
	rsGraph = {}
	
	#Only do the restructuring if this graph contains all the fields to be restructured
	missingField = None
	for field in inputFields:
		if not inputGraph.has_key(field):
			return inputGraph
	
	outputStructure = {
		'frbr:partOf': {
			'rdf:type': 'fabio:JournalIssue',
			'prism:issue': inputGraph['prism:issue'],
			'frbr:partOf': {
				'rdf:type': 'fabio:JournalVolume',
				'prism:volume': inputGraph['prism:volume'],
				'frbr:partOf': {
					'rdf:type': 'fabio:Journal',
					'fabio:hasTitle': inputGraph['__journalTitle']
				}
			}
		}
	}
	
	# Write the output structure to our new graph
	for field in outputStructure.keys():
		rsGraph[field] = outputStructure[field]
		
	#Remove the restructured fields from inputGraph
	for field in inputFields:
		del inputGraph[field]
		
	#Now add all the remaining inputfields to the restructured graph
	for field in inputGraph.keys():
		rsGraph[field] = inputGraph[field]
	
	return rsGraph