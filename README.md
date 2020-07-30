# LocalGlobal

This repository contains code to process the output of the [WikiRevParser](https://github.com/ajoer/WikiRevParser) for analysis of location/cultural bias in Wikipedia articles in different languages. 

The code relies on two main packages:

* my [WikiRevParser package](https://github.com/ajoer/WikiRevParser)
* my forked and re-worked version of the [Wikipedia API wrapper](https://github.com/ajoer/Wikipedia)

The code is open source and free to use under the MIT license

See visualization output examples, how to run and repo overview below.

## Visualization output examples

The repository outputs visualizations of the relationship between local and non-local entities and/or references. Here are a few examples:

1. Entities in the Arabic COVID-19 pandemic page on Wikipedia:

![Arabic](/visualizations/entities/ar.png)

2. References in the Danish COVID-19 pandemic page on Wikipedia:

![Danish](/visualizations/references/da.png)

2. Both entities and references in the Dutch COVID-19 pandemic page on Wikipedia:

![Danish](/visualizations/nl.png)

## How to run

All files can be run with python3 (tested). Comparability with earlier versions is unknown. Should be run from main repository

    $ python3 process_raw_data.py --language --check_os
    $ python3 get_locations.py --language --check_os
    $ python3 make_countries_per_language_list.py
    
    
## Repository overview
The repository is structured as follows:

**[code/](https://github.com/ajoer/LocationBias/tree/master/code)** contains all the code of the project.

  * [process_raw_data.py](https://github.com/ajoer/LocationBias/blob/master/code/process_raw_data.py) takes the output from the [WikiRevParser](https://github.com/ajoer/WikiRevParser) as input and aggregates the data from the individual revisions to represent each week once. 
  This is necessary for cross-cultural comparison and significantly improves runtime without losing analysis possibilities. 
  The file outputs the data in the same format as it read it in, but with one entry in the JSON for each week (7 day spans from the first revision).  
  * [utils.py](https://github.com/ajoer/LocationBias/blob/master/code/utils.py) is a general utilities file.
  * [get_locations.py](https://github.com/ajoer/LocationBias/blob/master/code/get_locations.py) is the main processing script here. 
  It reads in the weekly revision history data in [data/covid19/weekly](https://github.com/ajoer/LocationBias/tree/master/data/covid19/weekly) as outputted by [process_raw_data.py](https://github.com/ajoer/LocationBias/blob/master/code/process_raw_data.py), and assigns location to all blue links and references in a revision of a Wikipedia page, if locations can be assigned. The file outputs a dictionary for each Wikipedia page with locations for each timestamp to the [data/covid19/processed](https://github.com/ajoer/LocationBias/tree/master/data/covid19/processed) folder.
  * [make_analysis.py](https://github.com/ajoer/LocationBias/blob/master/code/make_analysis.py) is work in progress, and will eventually output analyses and visualizations on the location/culture bias in Wikipedia pages.
  * [make_countries_per_language_list.py](https://github.com/ajoer/LocationBias/blob/master/code/make_countries_per_language_list.py) is a preprocessing file that makes a dataset of countries for each language. The output is a JSON dictionary with language codes as keys with lists of countries as values. It reads in the ["countries_w_language.tsv" file](https://github.com/ajoer/LocationBias/blob/master/resources/countries_w_language.tsv) and produces the [countries_per_language.json file](https://github.com/ajoer/LocationBias/blob/master/resources/countries_per_language.json). The script is only run if the later file does not exist yet. 
  * [wikidata_queries.txt](https://github.com/ajoer/LocationBias/blob/master/code/wikidata_queries.txt) is a file with SPARQL queries for Wikidata that are used previously or actively in this project (in code or in the [Wikidata query API](https://query.wikidata.org/)).
 
**[data/covid19/](https://github.com/ajoer/LocationBias/tree/master/data/covid19)** is a data repository with data created by the code in [process_raw_data.py](https://github.com/ajoer/LocationBias/blob/master/code/process_raw_data.py) and [get_locations.py](https://github.com/ajoer/LocationBias/blob/master/code/get_locations.py).

**[resources/](https://github.com/ajoer/LocationBias/tree/master/resources)** contains the resources used in this project, namely the files related to countries per language.

**[visualizations/](https://github.com/ajoer/LocationBias/tree/master/visualizations)** contains the visualization outputs from the code. There are three types of visualizations at present: visualizations of entities (blue links), references or both. 
Examples of visualizations are shown above. 

## Acknowledgements
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No 812997.