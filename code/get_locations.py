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

