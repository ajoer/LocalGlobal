#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 

	Assign location to all (location) links and references in a revision of a Wikipedia page.

	NB: this really should only take NERs and not all entities... (slange is assigned to Sweden and skat to Russia)
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
from geopy.geocoders import Nominatim
from geoprovenance.py import gputils, gpinfer

parser = argparse.ArgumentParser(description='''''')
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--check_os", default="y")

args = parser.parse_args()

directory = "data/covid19/weekly/*.json"
geolocator = Nominatim(user_agent="LocalGlobal")
inferrer = gpinfer.LogisticInferrer()

def make_countries_list():
	countries = set()
	for list_of_countries in list(countries_per_language.values()):
		for country in list_of_countries:
			countries.add(country)
	return countries

countries_per_language = utils.read_from_json("resources/countries_per_language.json")
countries = make_countries_list()

link_locations_holder = {}
reference_locations_holder = {}

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

def wikidata_query(query):
	
	result = utils.query_wikidata(query)

	if result.empty != True:
		countrylabels = [c.lower() for c in result["countryLabel.value"]]
		return ''.join(countrylabels[0])
	else: 
		return None

def plot_joint_development(language, timestamps, data): 

	fig, ax = plt.subplots()
	ax.plot(timestamps, data["links_local"], label="links local", color="indianred", linestyle="dashed")
	ax.plot(timestamps, data["links_non_local"], label="links non-local", color="steelblue", linestyle="dashed")
	ax.plot(timestamps, data["references_local"], label="references local", color="indianred", linestyle="dotted")
	ax.plot(timestamps, data["references_non_local"], label="references non-local", color="steelblue", linestyle="dotted")
	ax.legend(loc="best")

	plt.xticks(timestamps, timestamps, rotation='vertical')
	plt.margins(0.2)
	
	plt.savefig(f"visualizations/{language}.png")

def plot_development(language, timestamps, local, non_local, output_location):

	fig, ax = plt.subplots()
	ax.plot(timestamps, local, label="local", color="indianred", linestyle="dashed")
	ax.plot(timestamps, non_local, label="non-local", color="steelblue")
	ax.legend()
	
	plt.xticks(timestamps, timestamps, rotation='vertical')
	plt.margins(0.2)
	
	plt.savefig(f"visualizations/{output_location}/{language}.png")


def estimate_localness(countries, language):
	#print("estimating localness for %s countries" % len(countries))
	local = 0
	non_local = 0

	countries4language = set(countries_per_language[language])
	for country in countries:
		if country in countries4language:
			#print("\tlocal\t", country)
			local += 1
		else:
			#print("non local\t\t", country)
			non_local += 1
	return local, non_local


def get_links_locations(links, language):
	# add support for adjectives and genitive, e.g. "danske" and "danmarks"
	link_locations = []

	for link in links: 
		#print("----------")
		#print(link)

		if any(i.isdigit() for i in link): continue
		if len(link) == 0: continue
		if link == "coronavirus": continue

		country = None

		if link in set(link_locations_holder.keys()):
			country = link_locations_holder[link]
			link_locations.append(country)
			#print(1, link, "\t",  country)

		try:
			if link in countries:
				country = link
				link_locations_holder[link] = country
				link_locations.append(country)
				#print(2, link, "\t",  country)
		except KeyError: continue

		if country == None:
			estimated_country = geolocator.geocode(link)
			if estimated_country:
				country = estimated_country.lower()

				if country not in countries: continue
				#print(3, link, "\t", country)
				link_locations_holder[link] = country
				link_locations.append(country)

			else: 
				country = wikidata_query(country4person % link.title())
				if country == None: continue
				link_locations_holder[link] = country
				link_locations.append(country)
				#print("PERSON", link, "\t", country)

	return link_locations


def get_reference_locations(references):
	reference_locations = []

	#print("number of references:\t", len(references))

	for reference in references:

		if reference in set(reference_locations_holder.keys()):
			country = reference_locations_holder[reference]
		else:
			(loc, country, dist) = inferrer.infer(reference)
			if country not in countries: continue
			reference_locations_holder[reference] = country
		reference_locations.append(country)
	#print("done with references")
	return reference_locations

def main():

	all_references_origin = Counter()
	all_links_origin = Counter()

	for filename in sorted(glob.glob(directory)):

		language = filename.split("/")[-1].split(".")[0]
		if args.language:
			if language != args.language: continue

		print(f"\nLanguage:\t{language}")

		if args.check_os == "y":
			if (
				os.path.isfile(f"visualizations/entities/{language}.png") and 
				os.path.isfile(f"visualizations/references/{language}.png")
			):
				print(f"{language} has already been analyzed, moving on...")
				continue
	
		if language not in set(countries_per_language.keys()): 
			#print(f"There is no country listed for {language}")
			continue

		input_data = utils.read_from_json(filename)
		
		output_data = {
			"days": [],
			"links_local": [],
			"links_non_local": [],
			"references_local": [],
			"references_non_local": []
		}

		days = sorted(input_data.keys())

		previous_references = []
		previous_links = []

		references_origins = Counter()
		links_origins = Counter()

		for n, day in enumerate(days):
			#print("Processing day %s of %s (%s)" % (n, len(days), day))

			output_data["days"].append(str(day))

			# links
			#print("links")
			links = input_data[day]["links"]
			if sorted(links) == sorted(previous_links):
				output_data["links_local"].append(output_data["links_local"][-1])
				output_data["links_non_local"].append(output_data["links_non_local"][-1])
			
			else:
				link_countries = get_links_locations(links, language)
				links_local, links_non_local = estimate_localness(link_countries, language)
				output_data["links_local"].append(links_local)
				output_data["links_non_local"].append(links_non_local)

			previous_links = links

			# references
			#print("references")
			references = input_data[day]["references"]
			if sorted(references) == sorted(previous_references):
				output_data["references_local"].append(output_data["references_local"][-1])
				output_data["references_non_local"].append(output_data["references_non_local"][-1])

			else:
				references_countries = get_reference_locations(references)
				references_local, references_non_local = estimate_localness(references_countries, language)
				output_data["references_local"].append(references_local)
				output_data["references_non_local"].append(references_non_local)
			
			previous_references = references

			if n == len(days)-1:

				print(f"links origins for {language}", Counter(link_countries).most_common(10))
				print(f"reference origins for {language}", Counter(references_countries).most_common(10))
				print()

				all_links_origin.update(link_countries)
				all_references_origin.update(references_countries)


		plot_joint_development(language, output_data["days"], output_data)
		plot_development(language, output_data["days"], output_data["links_local"], output_data["links_non_local"], "entities")
		plot_development(language, output_data["days"], output_data["references_local"], output_data["references_non_local"], "references")
		utils.save_to_json(language, "output", output_data)
		

if __name__ == "__main__":
	main()