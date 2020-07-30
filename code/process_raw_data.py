#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 
	Aggregate data from revisions to represent each a week. 
	All revisions are read, grouped in days, and they grouped in one day for each week. 
	Output: dictionary with dates as keys, links and references as values
"""

import argparse
import glob
import json
import os
import utils

from collections import OrderedDict
from datetime import datetime
from datetime import timedelta

parser = argparse.ArgumentParser(description='''''')
parser.add_argument("--language", help="e.g. 'nl' (for debugging).")
parser.add_argument("--check_os", default="n")

args = parser.parse_args()

input_directory = "data/covid19/raw/*.json"

def addORremove_links(data, add_remove):
	if add_remove == "add":
		key = "new_links"
	else:
		key = "deleted_links"
	try:
		links = []
		for link in data[key]:
			links.append(link)
		return links
	except KeyError:
		return None


def get_day_data(data):
	current_date = datetime.now().date()
	timestamps = OrderedDict(data).keys()
	day_data = OrderedDict()

	for n,timestamp in enumerate(timestamps):
		d = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").date()

		if n == 0:
			current_date = d
			day_data[d] = {"links": [], "references": []}

		if d != current_date:
			day_data[d] = {"links": [], "references": []}
			day_data[d]["links"] = day_data[current_date]["links"]
			current_date = d

		new_links = addORremove_links(data[timestamp], "add")	
		if new_links != None:
			day_data[d]["links"] += new_links

		delete_links = addORremove_links(data[timestamp], "remove")
		if delete_links != None:
			day_data[d]["links"] = list(set(day_data[d]["links"]) - set(delete_links))
		
		day_data[d]["references"] = data[timestamp]["citations"]
	return day_data

def get_week_data(day_data):
	days = sorted(day_data.keys())
	week_data = OrderedDict()

	current_week_date = ''
	next_week_date = ''

	for day in days:

		if day == days[0]:
			current_week_date = day
			week_data[day] = day_data[day]
			next_week_date = current_week_date + timedelta(days=7)

		elif day < next_week_date:
			add_links = list(set(day_data[day]["links"])-set(week_data[current_week_date]["links"]))
			remove_links = list(set(week_data[current_week_date]["links"])-set(day_data[day]["links"]))
			week_data[current_week_date]["links"] + add_links
			for link in remove_links:
				week_data[current_week_date]["links"].remove(link)

			add_references = list(set(day_data[day]["references"])-set(week_data[current_week_date]["references"]))
			remove_references = list(set(week_data[current_week_date]["references"])-set(day_data[day]["references"]))
			week_data[current_week_date]["references"] + add_references
			for references in remove_references:
				week_data[current_week_date]["references"].remove(references)

		elif day >= next_week_date:
			current_week_date = day
			week_data[day] = day_data[day]
			next_week_date = next_week_date + timedelta(days=7)

	for day in sorted(week_data):
		week_data[str(day)] = week_data.pop(day)
	return week_data

def main():
	for filename in sorted(glob.glob(input_directory)):

		language = filename.split("/")[-1].split(".")[0]
		if args.language:
			if language != args.language: continue

		print("\nLanguage:\t", language)

		if args.check_os == "y":
			if os.path.isfile(f"data/weekly/{language}.png"):
				print(f"{language} has already been processed, moving on...")
				continue

		input_data = utils.read_from_json(filename)

		day_data = get_day_data(input_data)
		week_data = get_week_data(day_data)
		utils.save_to_json(language, "weekly", week_data)
		print("done")

if __name__ == "__main__":
	main()