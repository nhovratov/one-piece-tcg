from pathlib import Path
import json

cardDb = {}
pathlist = Path('./card-db').glob('**/*.json')
for path in pathlist:
	path_in_str = str(path)
	readFile = open(path_in_str, 'r')
	card = json.load(readFile)[0]
	addCard = {
		'code': card['card_id'],
		'type': card['category'],
		'color': card['color'],
		'attribute': None if card['attribute'] is None else card['attribute'].split('/'),
		'life': card['life'],
		'cost': card['cost'],
		'power': card['power'],
		'counter': 0 if card['counter'] is None else card['counter'],
		'name': card['name'],
		'archetype': None if card['type'] is None else card['type'].split('/'),
		'effectText': card['effect'],
		'trigger': card['trigger']
	}
	cardDb[addCard['code']] = addCard

pathlist = Path('./card-effects').glob('**/*.json')
for path in pathlist:
	path_in_str = str(path)
	readFile = open(path_in_str, 'r')
	effect = json.load(readFile)
	pathParts = path_in_str.split('/')
	lastPart = pathParts[-1:][0]
	cardId = lastPart[:-5]
	cardDb[cardId] = {**cardDb[cardId], **effect}

jsonData = json.dumps(cardDb)
f = open('card-db.json', 'w')
f.write(jsonData)
