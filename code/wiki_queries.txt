all_countries_with_language_in_all_languages = """
SELECT ?lcode ?label 
WHERE
{
  ?country wdt:P37 ?language .
  ?country wdt:P31 wd:Q6256.
  ?country rdfs:label ?label .
  ?language wdt:P424 ?lcode
  
}"""

all_countries_in_all_languages = """
SELECT ?label
WHERE
{
  ?country wdt:P31 wd:Q6256.
  ?country rdfs:label ?label
}"""

countries_query = """
	SELECT ?country ?countryLabel 
	WHERE 
	{ 
		?country wdt:P31 wd:Q6256 . 
		SERVICE wikibase:label 
		{ bd:serviceParam wikibase:language "%s". }
	}
	group by ?country ?countryLabel"""

countries4language_query = """
	SELECT DISTINCT ?country ?countryLabel
	WHERE 
	{
		?country wdt:P37 ?officiallanguage .
		?country wdt:P31 wd:Q6256 .
		?officiallanguage wdt:P424 "%s" .
		?country rdfs:label ?countryLabel . FILTER(lang(?countryLabel)='en')
	}
	"""