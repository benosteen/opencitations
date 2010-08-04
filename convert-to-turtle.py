"""
convert-to-turtle.py 

Read RDF data in XML or any triples format, does some cleanup, and outputs as Turtle RDF
"""

import sys, re, os
from read_triples import read_triples
from namespace_authorities import get_nsAuthorities
from output_vocabulary import get_vocabulary
from dir_navigator import Walk

#Provide command-line arguments: input-file, input-format
if not len(sys.argv)==3:
	sys.exit("Program requires two command-line arguments: 1) top-level directory for source data; 2) source file format\n")

sourceDir = sys.argv[1]
inputFormat = sys.argv[2]

print "Source directory: " + str(sourceDir) + "..."
print "Input format: " + str(inputFormat) + "..."
if not re.search('(xml|triple)', inputFormat, re.IGNORECASE):
	sys.exit("Input format can't be identified\n")

# Go through source directoy structure, making transformed version of every source file
sourceFiles = [] 
if re.search('xml', inputFormat, re.IGNORECASE):
	sourceFiles = Walk(sourceDir, 1, '^.+\.n?xml$')
elif re.search('triple', inputFormat, re.IGNORECASE):
	sourceFiles = Walk(sourceDir, 1, "^.+.txt$")
	
outputDir = re.sub('/$', '', sourceDir)
outputDir = outputDir + '_Turtle-RDF/'
	
for inputFileName in sorted(sourceFiles):
	print "Doing file: " + str(inputFileName) + "..."

	#Output filename is same as input, but with changed top-level directory, and changed file extension
	outputFileName = re.sub(sourceDir, outputDir, inputFileName)
	outputFileName = re.sub('\.(txt|xml|nxml)$', '', outputFileName)
	outputFileName = outputFileName + ".n3"
	
	outputPath = re.sub('/[^/]+$', '/', outputFileName)
	#print outputPath
	if not os.path.isdir(outputPath):
		os.makedirs(outputPath) #NB this function makes all intermediate dirs as required
	
	#Filehandles
	inputFile = open(inputFileName, 'r')
	outputFile = open(outputFileName, 'w')

	#Print a header to the output file
	outputFile.write ("""######
	## Turtle RDF data, generated using convert-to-turtle.py 
	## at the Open Citations Project, Image Bioinformatics Research Group,
	## University of Oxford. See http://ibrg.zoo.ox.ac.uk
	######

	""")
	outputFile.write ("## Source file: " + str(inputFileName) + "\n\n")

	#Get namespace authorities from separate manifest
	authorities = get_nsAuthorities()

	#List all the authority prefixes at the top of the output file
	for auth in sorted(authorities.keys()):
		outputFile.write("@prefix\t" + authorities[auth] + "\t<" + auth + ">.\n")

	outputFile.write("\n")


	#Read the inputFile in to a triples dictionary. In fact it will be a multidimensional dictionary, taking the form triples[subject][predicate]
	triples = read_triples(inputFile, inputFormat, authorities)


	# Output rdf hash in standard Turtle format
	for subject in sorted(triples.keys()):
		outputFile.write(subject + "\n")
		
		#Add an rdf:type to all journal article and author graphs, if they don't have one
		if not triples[subject].has_key('entityType') or triples[subject].has_key('rdf:type'):
			if triples[subject].has_key('artTitle'):
				triples[subject]['entityType'] = ['fabio:Article']
			elif triples[subject].has_key('authorMainName'):
				triples[subject]['entityType'] = ['foaf:Person']
		
		pos = 0 #position as we cycle through the list of keys
		for predicate in sorted(triples[subject].keys()):
			values = triples[subject][predicate]
			# # # Here we are going to make sure the output value is a string
			if type(values).__name__=='dict':
				valueList = []
				for key in values.keys():
					value = 0
					if type(values[key]).__name__=='str':
						value = values[key]
					elif type(values[key]).__name__=='list':
						value = str(", ".join(values[key]))
					displayKey = str(get_vocabulary(key))
					valueList.append(displayKey + ' "' + value + '"')
				valueString = "[\n\t\t" + str(";\n\t\t".join(valueList)) + "\n\t]"
				values = valueString
			if type(values).__name__=='str':
				values = values #It's already a string
			elif type(values).__name__=='list':
				values = str(", ".join(values))
			else:
				print "Couldn't estbalish data type for output value: " + str(type(values).__name__)
			# # #
				
			displayPredicate = str(get_vocabulary(predicate))
			outputFile.write("\t" + displayPredicate + "\t" + values)
			
			#Last one should be followed by full stop
			if pos + 1 == len(triples[subject].keys()):
				outputFile.write(".\n\n")
			
			#All others use a semi-colon
			else:
				outputFile.write(";\n")
			
			pos += 1
		

	inputFile.close()
	outputFile.close()