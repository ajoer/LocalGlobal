#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 
	Produce a dictionary of languages per country. 
	Output: dictionary where keys are language codes and values are list of countries where the language is spoken
	Input is a list of countries and the languages spoken there.
"""
import json

data = open("resources/countries_w_language.tsv").readlines()

dictionary = {}
for line in data:
	country, languages = line.strip().split('\t')
	for l in languages.split(","):
		l = l.strip()
		if l not in set(dictionary.keys()):
			dictionary[l] = []
		dictionary[l].append(country.lower())

file_name = f"resources/countries_per_language.json"
with open(file_name, 'w', encoding='utf8') as outfile:
	json.dump(dictionary, outfile, sort_keys=True, default=str, indent=4, ensure_ascii=False)