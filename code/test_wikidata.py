import utils

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

countries = get_countries("an")
print(countries)