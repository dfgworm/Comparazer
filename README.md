This repository includes a bunch of scraped examples: files prefixed with "names_" contain names and number of occurences of these names in scraped texts, while files with "weights_" contain same names sorted by sentiment, taken from the internet.

Note that "book characters" contain a lot of writers as well, because they both occur in the same context. This is a known issue which is not easy to fix. Otherwise algorithm works pretty accurately, at about 95% accuracy.

# Comparazer

A spider-crawler written in Python with use of Scrapy and Spacy.
It's main objective is to scrape a bunch of texts with a given thematic, for example "football players", extract names from it, then scrape sentiment on those names from internet and sort them by these sentiments.

It's functionality is divided into 2 parts: Extractor and Affirmator.

Extractor simply extracts names from texts on sites and saves them.

Affirmator then sorts and cleans those names, selects most frequent ones and scrapes even more text on those specific names to get some sentiment on them. It then sorts by their 'sentiment' points and saves them.
