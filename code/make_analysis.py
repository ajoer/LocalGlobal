#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 
	-- Locality bias analysis and visualization scripts -- 
	Analyse links and references from revisions of pages in language versions on Wikipedia for locality bias.
	Evaluate whether a country is local to a language. Make visualizations (heatmaps and plots of temporal development).
	Produce statistical analysis.
	Output ?? 
	Input: dictionary with countries assigned to all links and references for each week in the revision history of a Wikipedia page.
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
