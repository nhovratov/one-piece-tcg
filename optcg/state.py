import optcg.info as info

game = {
    'turn': 0,
    'playerTurn': None,
    'player1': {},
    'player2': {}
}

def create(deck1, deck2):
    game['player1'] = create_player_state(deck1)
    game['player2'] = create_player_state(deck2)

def create_player_state(deck):
    return {
        'deck': deck['deck'],
        'leader': deck['leader'],
        'field': {
            'leader': {
                'code': deck['leader'],
                'status': 'active',
                'powerIncreaseBattle': 0,
                'attachedDon': 0,
            },
            'stage': {},
            'characters': [],
            'don': {'active': 0, 'rested': 0}
        },
        'hand': [],
        'trash': [],
        'life': [],
        'don_deck': 10,
        'battleEffects': []
    }

def get_hand(player):
    return game[player]['hand']

def get_card(player, index):
    return game[player]['hand'][index]

def get_number_of_cards_in_hand(player):
    return len(get_hand(player))

def get_leader(player):
    return game[player]['field']['leader']

def get_life_count(player):
    return len(game[player]['life'])

def getAvailableDon(player):
    return game[player]['field']['don']['active']

def getRestedDon(player):
    return game[player]['field']['don']['rested']

def getNumberOfPlayerCharacters(player):
    return len(game[player]['field']['characters'])

def get_turn_player():
    return game['playerTurn']

def get_don_deck(player):
    return game[player]['don_deck']

def get_overall_don(player):
    return 10 - get_don_deck(player)

def character_exists_at_index(player, index):
    return index < len(get_characterList(player))

def get_character(player, index):
    character_list = get_characterList(player)
    return character_list[index]

def get_characterList(player):
    return game[player]['field']['characters']

def get_game_turn():
    return game['turn']

def get_don_power(player, character):
    return getAttachedDon(character) * 1000 if player == get_turn_player() else 0

def getAttachedDon(character):
    return character['attachedDon']

def get_character_base_power(character):
    code = character['code']
    card_info = info.get_card_info(code)
    basePower = card_info['power']
    return basePower

def get_character_power(player, character):
    basePower = get_character_base_power(character)
    donPower = get_don_power(player, character)
    power = basePower + donPower
    return power

def get_leader_power(player):
    leader = get_leader(player)
    return get_character_power(player, leader)

def hand_card_exists_at_index(player, index):
    return index < len(get_hand(player))

def isCharacterRested(player, index):
    return game[player]['field']['characters'][index]['status'] == 'rested'

def getNumberOfActiveCharacters(player):
    activeCharacters = [character for character in game[player]['field']['characters'] if character['status'] == 'active']
    return len(activeCharacters)