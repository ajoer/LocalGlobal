#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 

	this is just for small pieces of test code. Delete when needed
"""

import utils

country4person = """
	SELECT ?country ?countryLabel WHERE
	{
	  ?entity rdfs:label "%s"@%s .
	  ?entity wdt:P31 wd:Q5 .
	  ?entity wdt:P27 ?country 
	  SERVICE wikibase:label 
	  { bd:serviceParam wikibase:language "%s". }
	}
	"""

def wikidata_query(query):
	
	result = utils.query_wikidata(query)

	if result.empty != True:
		countrylabels = [c.lower() for c in result["countryLabel.value"]]
		print(''.join(countrylabels[0]))
		return countrylabels
	else: 
		return None


# country = wikidata_query(country4person % ("Karen-Helene Hjort", "en", "en"))
# country = wikidata_query(country4person % ("Karen-Helene Hjort", "da", "da"))

countries_per_language = utils.read_from_json("resources/countries_per_language.json")

def estimate_localness(countries, language):
	print("estimating localness for %s countries" % len(countries))
	local = 0
	non_local = 0

	countries4language = set(countries_per_language[language])
	for country in countries:
		if country in countries4language:
			print("\tlocal\t\t", country)
			local += 1
		else:
			print("non local\t\t", country)
			non_local += 1
	return local, non_local


c = ["germany", "holland", "denmark"]
l = "da"
estimate_localness(c,l)