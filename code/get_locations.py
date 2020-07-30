#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 

	Assign location to all (location) links and references in a revision of a Wikipedia page.

	NB: this really should only take NERs and not all entities... This has gotten better after I dropped the geopy package

"""

import argparse
import glob
import json
import matplotlib.pyplot as plt
import os
import re
import string
import utils

from collections import Counter, defaultdict, OrderedDict
from datetime import datetime
from datetime import timedelta
# from geopy.geocoders import Nominatim #(discarted because it severly overtriggers. "dyr" ==> Russia, "slange" ==> Sweden)
from geoprovenance.py import gputils, gpinfer

parser = argparse.ArgumentParser(description='''''')
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--check_os", default="y")

args = parser.parse_args()

directory = "data/covid19/weekly/*.json"
#geolocator = Nominatim(user_agent="LocalGlobal")
inferrer = gpinfer.LogisticInferrer()

def make_countries_list():
	countries = set()
	for list_of_countries in list(countries_per_language.values()):
		for country in list_of_countries:
			countries.add(country)
	return countries

countries_per_language = utils.read_from_json("resources/countries_per_language.json")
countries = make_countries_list()

country_nicknames = {
	"people's republic of china": "china",
	"kingdom of denmark": "denmark",
	"kingdom of the netherlands": "the netherlands",
	"united states of america": "united states",
	"usa": "united states",
	"uk": "united kingdom",
	"great britain": "united kingdom"
}

links_locations_holder = {}
references_locations_holder = {}

bad_words = ["coronavirus", "protein", "pandemic", "isolation", "dr", ]
country4person = """
	SELECT ?country ?countryLabel WHERE
	{
	  ?entity rdfs:label "%s"@en .
	  ?entity wdt:P31 wd:Q5 .
	  ?entity wdt:P27 ?country 
	  SERVICE wikibase:label 
	  { bd:serviceParam wikibase:language "en". }
	}
"""
country4entity = """
	SELECT ?country ?countryLabel WHERE
	{
	  ?entity rdfs:label "%s"@%s .              
      ?entity wdt:P17 ?country .
	  SERVICE wikibase:label 
	  { bd:serviceParam wikibase:language "en". }
	}
"""

def wikidata_query(query):
	
	result = utils.query_wikidata(query)

	if result.empty != True:
		return ''.join(result["countryLabel.value"][0].lower()) #countrylabels[0])
	else: 
		return None

def get_links_locations(links, previous_links, previous_links_locations, language):
	# add support for adjectives and genitive, e.g. "danske" and "danmarks"
	
	timestamps_output = {}

	if links == previous_links:
		print("Reusing previous link locations")
		return previous_links_locations
	
	previous_links = set([link for country in set(previous_links_locations.keys()) for link in previous_links_locations[country]])

	if len(links) == len(set(links)):
		links = set(links)

	for link in links: 

		if any(i.isdigit() for i in link): continue
		if len(link) == 0: continue
		if link in bad_words: continue

		link = link.strip()
		country = None

		if link in set(links_locations_holder.keys()):
			country = links_locations_holder[link]

		elif link in countries:
			country = link

		# elif link in previous_links:
		# 	for country in set(previous_links_locations.keys()):
		# 		if link in previous_links_locations[country]:
		# 			country = country
		# 			break

		elif country == None:
			country = wikidata_query(country4entity % (link.title().strip(), language))
			if country == None: 
				country = wikidata_query(country4person % link.title())
				if country == None: continue

		# make entries uniform, e.g. "united states" => "usa"
		if country in set(country_nicknames.keys()):
			country = country_nicknames[country]

		if country not in set(timestamps_output.keys()):
			timestamps_output[country] = []

		links_locations_holder[link] = country	
		timestamps_output[country].append(link)

	return timestamps_output

def get_reference_locations(references, previous_references, previous_references_locations):
	references_locations = {}

	if references == previous_references:
		print("Reusing previous references")
		return previous_references_locations 

	if len(references) == len(set(references)):
		references = set(references)

	for reference in references:

		if reference in set(previous_references):
			for country in previous_references_locations:
				if reference in previous_references_locations[country]:
					country = country

		elif reference in set(references_locations_holder.keys()):
			country = references_locations_holder[reference]

		else:
			(loc, country, dist) = inferrer.infer(reference)
			if country not in countries: continue
			references_locations_holder[reference] = country
		
		if country in set(country_nicknames.keys()):
			country = country_nicknames[country]

		if country not in set(references_locations.keys()):
			references_locations[country] = []

		references_locations[country].append(reference)

	return references_locations

def main():

	for filename in sorted(glob.glob(directory)):

		language = filename.split("/")[-1].split(".")[0]
		if args.language:
			if language != args.language: continue

		print(f"\nLanguage:\t{language}")

		if args.check_os == "y":
			if os.path.isfile(f"data/covid19/processed/{language}.json"):
				print(f"{language} has already been analyzed, moving on...")
				continue
	
		if language not in set(countries_per_language.keys()): 
			continue

		input_data = utils.read_from_json(filename)
		output_data = {}
		days = sorted(input_data.keys())
		nr_days = len(days)
		if nr_days < 10: continue

		previous_links = []
		previous_links_locations = {}
		previous_references = []
		previous_references_locations = {}

		references_origins = Counter()
		links_origins = Counter()

		for n, day in enumerate(days):
			print("Processing day %s of %s:\t%s" % (n, nr_days, day))

			timestamps_output = {
				"links": {},
				"references": {}
			}

			links = sorted(input_data[day]["links"])
			references = sorted(input_data[day]["references"])

			links_countries = get_links_locations(links, previous_links, previous_links_locations, language) # dict
			timestamps_output["links"] = links_countries
			previous_links = links
			previous_links_locations = links_countries

			references_countries = get_reference_locations(references, previous_references, previous_references_locations)
			timestamps_output["references"] = references_countries
			previous_references = references
			previous_references_locations = references_countries
	
			#print("Completed day %s of %s" % (n, nr_days))
			#print(timestamps_output, "\n\n")
			output_data[day] = timestamps_output
		utils.save_to_json(language, "processed", output_data)

if __name__ == "__main__":
	main()

"""

def get_links_locations(links, previous_links_locations, language):
	# add support for adjectives and genitive, e.g. "danske" and "danmarks"
	
	timestamps_output = {}
	previous_links = sorted([y for x in previous_links_locations.values() for y in x])

	if links == previous_links:
		return previous_links_locations

	for link in links: 

		if any(i.isdigit() for i in link): continue
		if len(link) == 0: continue
		if link in bad_words: continue

		country = None

		if link in set(previous_links):
			for country in previous_links_locations:
				if link in previous_links_locations[country]:
					country = country

		elif link in set(links_locations_holder.keys()):
			country = links_locations_holder[link]

		elif link in countries:
			country = link
			links_locations_holder[link] = country

		elif country == None:
			country = wikidata_query(country4entity % (link.title().strip(), language))
			if country == None: 
				country = wikidata_query(country4person % link.title())
				if country == None: continue
				#country2 = wikidata_query(country4entity % (''.join([x.capitalize() for x in link.strip() if len(x) > 3]), language))

				# estimated_country = geolocator.geocode(link)
				# if estimated_country:
				# 	print(link)
				# 	print("geolocator country\t", estimated_country)
				# #if link == "who": link = "WHO"
			# 	country = estimated_country.lower()

			# 	if country not in countries: continue
				#print(3, link, "\t", country)
				#link_locations.append(country)

		# make entries uniform, e.g. "united states" => "usa"
		if country in set(country_nicknames.keys()):
			country = country_nicknames[country]

		links_locations_holder[link] = country	

		if country not in set(timestamps_output.keys()):
			timestamps_output[country] = []
		print(link, ":\t\t", country)
		timestamps_output[country].append(link)

	return timestamps_output


def main():
	# all_references_origin = Counter()
	# all_links_origin = Counter()

	for filename in sorted(glob.glob(directory)):

		language = filename.split("/")[-1].split(".")[0]
		if args.language:
			if language != args.language: continue

		print(f"\nLanguage:\t{language}")

		if args.check_os == "y":
			if os.path.isfile(f"data/covid19/processed/{language}.json"):
				print(f"{language} has already been analyzed, moving on...")
				continue
	
		if language not in set(countries_per_language.keys()): 
			#print(f"There is no country listed for {language}")
			continue

		input_data = utils.read_from_json(filename)
		output_data = {}
		days = sorted(input_data.keys())

		if len(days) < 10: continue

		previous_references = {}
		previous_links = {}

		references_origins = Counter()
		links_origins = Counter()

		for n, day in enumerate(days):
			if n != 0: print(days[n-1])
			#print("Processing day %s of %s (%s)" % (n, len(days), day))

			#output_data["days"].append(str(day))
			timestamps_output = {
				"links": {},
				"references": {}
			}

			links = sorted(input_data[day]["links"])
			references = sorted(input_data[day]["references"])

			# if links == previous_links:
			# 	timestamps_output["links"] = output_data[days[n-1]["links"]]
			# 	#output_data["links_local"].append(output_data["links_local"][-1])
			# 	#output_data["links_non_local"].append(output_data["links_non_local"][-1])
			
			links_countries = get_links_locations(links, previous_links_locations, language) # dict
			timestamps_output["links"] = links_countries
			previous_links = links_countries

			references_countries = get_reference_locations(references)
			timestamps_output["references"] = references_countries
			previous_references = references_countries
				# links_local, links_non_local = estimate_localness(link_countries, language)
				# output_data["links_local"].append(links_local)
				# output_data["links_non_local"].append(links_non_local)

				 
				
			# references
			#print("references")

			# if references == sorted(previous_references):
			# 	timestamps_output["references"] = output_data[days[n-1]]["references"]
			# 	# output_data["references_local"].append(output_data["references_local"][-1])
				# output_data["references_non_local"].append(output_data["references_non_local"][-1])


				# references_local, references_non_local = estimate_localness(references_countries, language)
				# output_data["references_local"].append(references_local)
				# output_data["references_non_local"].append(references_non_local)
			
			
			print(day)
			print(timestamps_output, )
			output_data[day] = timestamps_output
		# 	if n == len(days)-1:

		# 		print(f"links origins for {language}", Counter(link_countries).most_common(10))
		# 		print(f"reference origins for {language}", Counter(references_countries).most_common(10))
		# 		print()

		# 		all_links_origin.update(link_countries)
		# 		all_references_origin.update(references_countries)


		# plot_joint_development(language, output_data["days"], output_data)
		# plot_development(language, output_data["days"], output_data["links_local"], output_data["links_non_local"], "entities")
		# plot_development(language, output_data["days"], output_data["references_local"], output_data["references_non_local"], "references")
		utils.save_to_json(language, "processed", output_data)
"""