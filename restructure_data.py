def restructure_data (inputGraph):
	
	rsGraph = {}
	newStructures = {}
	
	#The re-structuring of some fields is dependent on others, hence the cascading dependencies
	pred = 'prism:issue'
	if inputGraph.has_key(pred):
		newStructures['frbr:partOf'] = {
			'rdf:type': 'fabio:JournalIssue',
			pred: inputGraph[pred]
		}
		del inputGraph[pred]
		
		pred = 'prism:volume'
		if inputGraph.has_key(pred):
			newStructures['frbr:partOf']['frbr:partOf'] = {
				'rdf:type': 'fabio:JournalVolume',
				pred: inputGraph[pred]
			}
			del inputGraph['prism:volume']
			
			pred = '__journalTitle'
			if inputGraph.has_key(pred):
				newStructures['frbr:partOf']['frbr:partOf']['frbr:partOf'] = {
					'rdf:type': 'fabio:Journal',
					'fabio:hasTitle': inputGraph[pred]
				}
				del inputGraph[pred]
				
				for pred in ('__journalIssnElectronic', '__journalIssnPrint', '__publisherName', '__journalIdInternal', '__pubmedJournalAbbrev'):
					if inputGraph.has_key(pred):
						newStructures['frbr:partOf']['frbr:partOf']['frbr:partOf'][pred] = inputGraph[pred]
						del inputGraph[pred]
	
	# Write the new structures to our new graph
	for field in newStructures.keys():
		rsGraph[field] = newStructures[field]
		
	#Now add all the remaining inputfields to the restructured graph
	for field in inputGraph.keys():
		rsGraph[field] = inputGraph[field]
	
	return rsGraph