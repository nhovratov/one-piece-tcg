import json

with open('card-db.json', 'r') as file:
    cardDatabase = json.load(file)

def get_card_info(card):
    return cardDatabase[card]

def hasRush(code):
    card_info = get_card_info(code)
    return card_info.get('hasRush', False)

def hasBlocker(code):
    card_info = get_card_info(code)
    return card_info.get('hasBlocker', False)

def sortCharactersByPower(character):
    info = get_card_info(character['code'])
    return info['power']

def getHumanReadableCharacterName(code):
    card_info = get_card_info(code)
    if card_info['type'] == 'character':
        name = '[' + code + '] ' + card_info['name'] + ' (' + str(card_info['cost']) + ')'
    else:
        name = '[' + code + '] ' + card_info['name']
    return name