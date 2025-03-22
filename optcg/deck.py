def create(name):
    blueprint = read('decks/' + name + '.deck')
    card_list = blueprint.splitlines()
    leader = card_list[0]
    leaderCard = extract_card_count(leader)['name']
    deck = []
    for card_definition in card_list[1:]:
        card_count = extract_card_count(card_definition)
        for i in range(0, card_count['number']):
            deck.append(card_count['name'])
    return {'leader': leaderCard, 'deck': deck}

def read(name):
    with open(name, 'r') as file:
        deck1_blueprint = file.read()
    return deck1_blueprint

def extract_card_count(card):
    position_x = card.find('x')
    number = int(card[0:position_x])
    name = card[(position_x + 1):]
    return {'number': number, 'name': name}