import csv
import json
import requests
import os

locales = ['en_UK']

gw_name_inaccuracies = {
    "Deathly Fortitude": "Deathly Fortune"
}

def main():
    gw_data = fetch_gw_data()
    cards = gw_to_cards(gw_data)
    gw_name_map = {}
    for c in cards:
        gw_name_map[c["name"]] = c

    csv_data = read_csv('cards-en_UK.csv')
    csv_name_map = {}
    for c in csv_data:
        name = c["name"]
        if name in gw_name_inaccuracies:
            name = gw_name_inaccuracies[name]
        if name not in gw_name_map:
            print("{} was not found in GW data!".format(name))
        hydrate_card_with_gw_data(c, gw_name_map[name])        
        csv_name_map[name] = c
    
    with open('cards-Missing.csv', 'w+') as missing_cards_csvfile:
        writer = csv.DictWriter(missing_cards_csvfile, fieldnames=cards[0].keys())
        writer.writeheader()
        for c in cards:
            if c["name"] not in csv_name_map:
                print("{} was not found in our data!".format(c["name"]))
                writer.writerow(c)

    with open('cards-en_UK.json', 'w+') as jsonfile:
        json.dump(csv_name_map.values(), jsonfile, sort_keys=True, indent=2)

    for c in csv_name_map.values():
        response = requests.get(c["image_url"], allow_redirects=True)
        image_folder = os.path.join('card_images')
        if not os.path.isdir(image_folder):
            os.makedirs(image_folder)
        filepath = os.path.join(image_folder, c["image_filename"])
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as imgfile:
                imgfile.write(response.content)


    

def hydrate_card_with_gw_data(card, gw):
    for key, value in gw.iteritems():
        # we skip "name" here cause that's our identifier. We don't want to stomp it, ever.
        if key != "name" and key in card and card[key] != gw[key]:
            print("GW data for '{}' differs from data stored in CSV:\n  GW:  {}: {}\n  CSV: {}: {}".format(card["name"], key, gw[key], key, card[key]))
            print("Skipping field.")
            continue

        card[key] = value

def fetch_gw_data():
    response = requests.get("https://warhammerunderworlds.com/wp-json/wp/v2/cards/?ver=13&per_page=1000")
    if response.status_code != 200:
        print("Error ({}) fetching GW data".format(response.status_code))
        return None
    
    return response.json()

def gw_to_cards(gw_data):
    return [create_card_from_gw(gw) for gw in gw_data]

# some names in GW data are '123. Foo' and others are just 'Foo'
def normalize_name(name):
    
    if '.' in name:
        name = '.'.join(name.split('.')[1:]).strip()
    return name.replace(u"\u2018", "'").replace(u"\u2019", "'").replace("&#8217;", "'").replace("&#8216;", "'")

def create_card_from_gw(gw):
    return {
        "gw_id": gw["id"],
        "name": normalize_name(gw["title"]["rendered"]),
        "gw_card_type_id": gw["card_types"][0],
        "gw_card_set_id": gw["sets"][0],
        "gw_warband_id": gw["warbands"][0],
        "gw_number": gw["acf"]["card_number"],
        "image_url": gw["acf"]["card_image"]["url"],
        "image_filename": gw["acf"]["card_image"]["filename"],
        "is_new": gw["acf"]["is_new"]
    }

def read_csv(csvpath):
    with open(csvpath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return [card for card in reader]

main()