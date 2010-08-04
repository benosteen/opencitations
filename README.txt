=================
==== README! ====
=================

[JBM, 2010-08-04]

Contents:
= Introduction
= Description
= Usage
= Requirements
= Components
= History

== INTRODUCTION ==

"Convert to Turtle" is a set of scripts for turning academic publishing source data into Turtle RDF as required for the Open Citations project.

It can accept triples (as dumped from a triplestore), or xml documents (as received from PubMed Central, for example).


== DESCRIPTION ==

The scripts attempt to be as flexible and configurable as possible, with regard to the xml datamodel of source input, and the required RDF vocabulary for the output.

At present output is only in Turtle format, however the production of output data is a fairly discrete function (see convert-to-turtle.py), with the intention that other output options could be easily added. All data is gathered from an input file in one phase, then all data is output in a second (much simpler) phase. If other output options were added, perhaps the program might change its name, as "turtle" would not longer be the sole aim.

Whatever the input format, the scripts aim to read the input in to a multi-dimensional dictionary object named "triples". It has these dimensions:
triples[subject][predicate][value]

That is to say, it has a data structure like:

triples = {
	subject1: {
		rdf:type value,
		pred1: value,
		pred2: value,
		pred3: value
	}
	subject2: {
		rdf:type value,
		pred1: value,
		pred2: value,
		pred3: value
	}
	subject3: {
		rdf:type value,
		pred1: value,
		pred2: value,
		pred3: {
			rdf:type value,
			predA: value,
			predB: value
		}
	}
}

The triples dictionary effectively stores named graphs for each of the following: the citing article, any cited articles, any authors of either citing or cited articles.

As each graph is created in the dictionary, it also makes sure that there is always an rdf:type triple.

It stores all the triples it can find in a single input file, then outputs them to an output file.

A subject must always be a unique string; predicates are also strings. Values can be either strings, lists of values, or even dictionaries containing a series of value pairs. At present, there are only dictionary objects at the value level in the case of authors' institutional affiliations. e.g.:

<e521c6bc72af384b9eec1843e2b8442e>
	rdf:type	foaf:Person;
	foaf:member	[
		rdf:type "foaf:Organization";
		dc:description "Tenovus Research Laboratory, Cancer Sciences Division, Southampton University, UK"
	];
	foaf:firstName	"M S";
	foaf:familyName	"Cragg".


== USAGE ==

To test the scripts, start at convert-to-turtle.py, which requires two command-line options:
[1] directory path where source data can be found;
[2] format of source data: (xml|triples)


== REQUIREMENTS ==

Developed using Python 2.5.2 in Cygwin / Windows. 

Performance with other versions of Python and OSs unknown.

The ElementTree package must be installed (http://effbot.org/zone/element-index.htm). This is an xml handler - probably not the best available. lxml is highly recommended, but was not used because I had trouble installing it for Cygwin.

Standard packages used are re, sys, os and hashlib - all of which are probably part of your basic Python installation.


== COMPONENTS ==

check_fulltext.py
check_knownAuthors.py
convert-to-turtle.py
dir_navigator.py

namespace_authorities.py
nlm_datamodel.py
output_vocabulary.py

[These three are all config files really. The provide discrete ways of: 
- configuring any namespace authorities to be listed in output (which also helps process PLoS triplestore dump); 
- configuring the "map" of xml elements to be extracted from in nlm xml; 
- configuring the controlled predicate vocabulary to be used on output]

rdf_string_cleanup.py
[This one is basically about getting the right carats and quote marks on the ends of things]

read_triples.py

sort_graphs.py
[Sorts the named graphs for output, so that a human reader inspecting the output will see things in an "expected" order.]


== HISTORY ==

The code has been developed by testing on a single PLoS triples file, and a sample of some thousands of PubMed Central xml files.