#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
data = open("resources/countries4languages.txt").readlines()

output = {}
all_countries = []

for line in data:
	elements = line.split(",")
	if len(elements) > 2: continue
	language_code, country = elements
	if language_code not in output.keys():
		output[language_code] = []
	if country not in output[language_code]:
		output[language_code].append(country.strip().lower())

with open("resources/language_w_country", 'w', encoding='utf8') as json_file:
    json.dump(output, json_file, sort_keys=True, indent=4, ensure_ascii=False)
