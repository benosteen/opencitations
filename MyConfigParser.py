from ConfigParser import ConfigParser

class MyConfigParser (ConfigParser):
	
	# modifies the get() method of ConfigParser
	def get(self, section, option, raw=False, vars=None): 
		
		# Options have to be un-escaped (if they are to be recognised as keys)
		optionTransform = [(':','&colon;'), ('[', '&lbrack;'),(']', '&rbrack;')] # extend as required
		for x,y in optionTransform: 
			option = option.replace(x,y) # do the replace stuff
		
		valueTransform = [('&lbrack;','['),('&rbrack;',']'),('&colon;',':')] # extend as required
		value = ConfigParser.get(self, section, option, raw, vars) # call the get() of ConfigParser
		for x,y in valueTransform: 
			value = value.replace(x,y) # do the replace stuff
		return value
	
	# modifies the options() method of ConfigParser
	def options(self, section): 
		repl = [('&lbrack;','['),('&rbrack;',']'),('&colon;',':')] # extend as required
		options = ConfigParser.options(self, section) # call the options() of ConfigParser
		newOptions = []
		for option in options:
			for x,y in repl: 
				option = option.replace(x,y) # do the replace stuff
			newOptions.append(option)
		return newOptions
		
	# overwrite the built in optionxform, that downcases the keys in the config
	def optionxform(self, optionstr):
		return optionstr