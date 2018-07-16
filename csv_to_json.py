import csv
import json

locales = ['en_UK']

for locale in locales:
    with open('{}.csv'.format(locale), 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        cards = [card for card in reader]
        with open('{}.json'.format(locale), 'w+') as jsonfile:
            json.dump(cards, jsonfile, sort_keys=True, indent=2)
        