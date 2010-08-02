#This is a manually maintained file, listing all the namespace authorities, and their prefixes, as required for correct reading of PLoS and other triplestore data

#These are authorities listed in the PLoS data, for which I am assigning prefixes:
def get_nsAuthorities ():
	authorities = {
		'http://purl.org/net/nknouf/ns/bibtex#': 'bibtex',
		'http://prismstandard.org/namespaces/1.2/basic/': 'prism',
		'http://rdf.plos.org/RDF/temporal#': 'plos-temporal',
		'http://rdf.plos.org/RDF/': 'plos',

#These are prefixes used, without any authority. I am assumng the following authorities:

		'http://purl.org/dc/terms/': 'dcterms',
		'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
		'http://rdf.topazproject.org/RDF/': 'topaz',
		
#Some others I added
		'http://xmlns.com/foaf/0.1/': 'foaf',
		'http://purl.org/net/fabio/': 'fabio',
		'http://purl.org/dc/elements/1.1/': 'dc'
	}
	return authorities