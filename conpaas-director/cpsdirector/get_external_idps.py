#!/usr/bin/python
import ConfigParser
import pprint

def get_external_idps(director_configfile):
    """
	get_external_idps(director_configfile)
	Checks in the conpaas section if the support_external_idp option is present and set.
	If so, checks if external_idps option is present, and for all 
	named idps collects all the options in the respective idp sections.
	Validation of option names and values n the idp sections is left to the calling program.
	Returns a dictonary with all idps and their options.
    """
    dict1 = {}
    Config = ConfigParser.ConfigParser()
    result = Config.read(director_configfile)
    if result == []:
        print 'Could not read %s' % filename
    idp_support = False # easy init
    external_idps = [] # easy init
    try:
	idp_support = Config.getboolean('conpaas', 'support_external_idp')
	if idp_support:
	    external_idps = Config.get('conpaas', 'external_idps').split(',')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
	print e
    if not idp_support:
        return dict1
    for xi in external_idps:
	options = [] # easy init
	try:
	    options = Config.options(xi)
	except ConfigParser.NoSectionError as e:
	    print e
	    continue # next xi
	dict2 = {}
	for option in options:
	    dict2[option] = Config.get(xi, option)
        dict1[xi] = dict2
    return dict1

if __name__ == '__main__':
    ei_dict = get_external_idps("/etc/cpsdirector/director.cfg")
    pprint.pprint(ei_dict)
