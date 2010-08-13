def restructure_data (inputGraph):
	
	rsGraph = {}
	newStructures = {}
	
	# # # # # # # # # # # # # # # # # # # # # # # # # # # #
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
			
			pred = '__sourceTitle'
			if inputGraph.has_key(pred):
				newStructures['frbr:partOf']['frbr:partOf']['frbr:partOf'] = {
					'rdf:type': 'fabio:Journal',
					'dc:title': inputGraph[pred]
				}
				del inputGraph[pred]
				
				for pred in ('prism:eIssn', 'prism:issn', 'dcterms:publisher', 'fabio:shortTitle'):
					if inputGraph.has_key(pred):
						newStructures['frbr:partOf']['frbr:partOf']['frbr:partOf'][pred] = inputGraph[pred]
						del inputGraph[pred]
				
				pred = '__journalIdInternal'
				if inputGraph.has_key(pred):
					newStructures['frbr:partOf']['frbr:partOf']['frbr:partOf']['dc:identifier'] = inputGraph[pred]
					del inputGraph[pred]
	
	# # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# If there is a volume number, but no issue number...
	elif inputGraph.has_key('prism:volume'):
		pred = 'prism:volume'
		newStructures['frbr:partOf'] = {
			'rdf:type': 'fabio:JournalVolume',
			pred: inputGraph[pred]
		}
		del inputGraph['prism:volume']
		
		pred = '__sourceTitle'
		if inputGraph.has_key(pred):
			newStructures['frbr:partOf']['frbr:partOf'] = {
				'rdf:type': 'fabio:Journal',
				'dc:title': inputGraph[pred]
			}
			del inputGraph[pred]
			
			for pred in ('prism:eIssn', 'prism:issn', 'dcterms:publisher', 'fabio:shortTitle'):
				if inputGraph.has_key(pred):
					newStructures['frbr:partOf']['frbr:partOf'][pred] = inputGraph[pred]
					del inputGraph[pred]
			
			pred = '__journalIdInternal'
			if inputGraph.has_key(pred):
				newStructures['frbr:partOf']['frbr:partOf']['dc:identifier'] = inputGraph[pred]
				del inputGraph[pred]
	
	
	# # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# When it is a chapter from a book
	elif inputGraph.has_key('__sourceTitle') and inputGraph.has_key('dc:title') and inputGraph['rdf:type'] != 'fabio:JournalArticle':
		newStructures['frbr:partOf'] = {
			'rdf:type': 'fabio:Document',
			'dc:title': inputGraph['__sourceTitle']
		}
		del inputGraph['__sourceTitle']
		
		if inputGraph.has_key('prism:edition'):
			newStructures['frbr:partOf']['prism:edition'] = inputGraph['prism:edition']
			del inputGraph['prism:edition']
	
	
	# # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# other unidentified __sourceTitle ...
	elif inputGraph.has_key('__sourceTitle') and inputGraph['rdf:type'] == 'fabio:JournalArticle':
		newStructures['frbr:partOf'] = {
			'rdf:type': 'fabio:Document',
			'dc:title': inputGraph['__sourceTitle']
		}
		del inputGraph['__sourceTitle']
	
	# # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# print publication vs epublication - separate "manifestations"
	pred = '__printPublicationYear'
	if inputGraph.has_key(pred):
		newStructures['frbr:embodiment'] = {
			'rdf:type': 'fabio:PrintObject',
			'fabio:hasPublicationYear': inputGraph[pred]
		}
		del inputGraph[pred]
	pred = '__ePublicationYear'
	if inputGraph.has_key(pred):
		if newStructures.has_key('frbr:embodiment'):
			newStructures['frbr:embodiment'] = [ newStructures['frbr:embodiment'], {
				'rdf:type': 'fabio:ComputerFile',
				'fabio:hasPublicationYear': inputGraph[pred]
			}]
		else: 
			newStructures['frbr:embodiment'] = {
				'rdf:type': 'fabio:ComputerFile',
				'fabio:hasPublicationYear': inputGraph[pred]
			}
		del inputGraph[pred]
	
	
	# # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# licence and copyright into blank nodes (beware spelling on licen(c|s)e!)
	pred = 'dcterms:licence'
	if inputGraph.has_key(pred):
		newStructures['dcterms:licence'] = {
			'rdf:type': 'dcterms:LicenceDocument',
			'rdf:value': inputGraph[pred]
		}
		del inputGraph[pred]
		
		pred = '__licenceURL'
		if inputGraph.has_key(pred):
			newStructures['dcterms:licence']['fabio:hasURL'] = inputGraph[pred]
			del inputGraph[pred]
	pred = 'dcterms:rights'
	if inputGraph.has_key(pred):
		newStructures['dcterms:rights'] = {
			'rdf:type': 'dcterms:RightsStatement',
			'rdf:value': inputGraph[pred]
		}
		del inputGraph[pred]
	
	
	# # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# Write the new structures to our new graph
	for field in newStructures.keys():
		rsGraph[field] = newStructures[field]
		
	#Now add all the remaining inputfields to the restructured graph
	for field in inputGraph.keys():
		rsGraph[field] = inputGraph[field]
	
	return rsGraph