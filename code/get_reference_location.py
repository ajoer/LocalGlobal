#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 

	Assign location to all (location) links and references in a revision of a Wikipedia page.

"""

import argparse
import glob
import gputils
import gpinfer
import json
import os
import matplotlib.pyplot as plt
import string
import re

from collections import Counter, defaultdict, OrderedDict
from geopy.geocoders import Nominatim

parser = argparse.ArgumentParser(description='''''')
parser.add_argument("topic", help="e.g. 'covid19'.")
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--visualize", default="n")
parser.add_argument("--check_os", default="y")

args = parser.parse_args()

directory = "../../data/%s/*.json" % args.topic
inferrer = gpinfer.LogisticInferrer()

def get_location(reference):
	(loc, dist) = inferrer.infer(reference)
	return (loc, dist)

def get_countries(language):
	countries_query = """
	SELECT ?country ?countryLabel 
	WHERE 
	{ 
		?country wdt:P31 wd:Q6256 . 
		SERVICE wikibase:label 
		{ bd:serviceParam wikibase:language "%s". }
	}
	group by ?country ?countryLabel"""
	result = utils.query_wikidata(countries_query % language)

	if result.empty != True:
		countries = result["countryLabel.value"]
		return [c.lower() for c in countries]
	else: return []

def get_countries4language(language):

	countries4language = []
	start = """
	SELECT DISTINCT ?country ?countryLabel
	WHERE 
	{
		?country wdt:P37 ?officiallanguage .
		?country wdt:P31 wd:Q6256 .
		?officiallanguage wdt:P424 """ 
	middle = "'" + language + "' . "
	end = """
		?country rdfs:label ?countryLabel . FILTER(lang(?countryLabel)='en')
	}
	"""
	result = utils.query_wikidata(start+middle+end)

	if result.empty != True:
		countries = result["countryLabel.value"]
		for cl in countries:
			print("country is %s" % cl)
			countries4language.append(cl.lower())
	else: 
	 	print("no country found for %s" % language)
	 	return None
	return countries4language

def main():

	int_countries = [x.strip() for x in open('../../data/countries.txt').readlines()]
	for filename in sorted(glob.glob(directory)):

		language = filename.split("/")[-1].split(".")[0]
		if args.language:
			if language != args.language: continue

		print("\nLanguage:\t", language)

		if args.check_os == "y":
			if os.path.isfile(f"visualizations/references/{language}.png"):
				print(f"{language} has already been analyzed, moving on...")
				continue

		input_data = json.load(open(filename))
		timestamps = list(input_data.keys())
		countries = get_countries(language) + int_countries
		countries4language = get_countries4language(language) # countries where they speak the language, e.g. local
		if countries4language == None: continue
		
		for timestamp in timestamps:
			local = 0
			non_local = 0 
			references = input_data[timestamp]["citations"]
			for reference in references:
				(loc, dist) = get_location(reference)
				print(loc, reference)


if __name__ == "__main__":
	main()