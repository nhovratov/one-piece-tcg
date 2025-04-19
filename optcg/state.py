import optcg.info as info

game = {
    'winner': None,
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
                'powerManipulationTurn': 0,
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

def get_trash(player):
    return game[player]['trash']

def get_card(player, index):
    return game[player]['hand'][index]

def get_number_of_cards_in_hand(player):
    return len(get_hand(player))

def get_leader(player):
    return game[player]['field']['leader']

def get_leader_or_character(player, leader_or_character):
    if leader_or_character == 'l':
        return get_leader(player)
    return get_character(player, int(leader_or_character))

def get_life_count(player):
    return len(game[player]['life'])

def get_available_don(player):
    return game[player]['field']['don']['active']

def get_rested_don(player):
    return game[player]['field']['don']['rested']

def get_number_of_player_characters(player):
    return len(game[player]['field']['characters'])

def get_turn_player():
    return game['playerTurn']

def get_don_deck(player):
    return game[player]['don_deck']

def get_overall_don(player):
    return 10 - get_don_deck(player)

def character_exists_at_index(player, index):
    return index < len(get_characters(player))

def get_character(player, index):
    character_list = get_characters(player)
    return character_list[index]

def get_characters(player):
    return game[player]['field']['characters']

def get_game_turn():
    return game['turn']

def get_don_power(player, character):
    return get_attached_don(character) * 1000 if player == get_turn_player() else 0

def get_attached_don(character):
    return character['attachedDon']

def get_character_base_power(character):
    code = character['code']
    card_info = info.get_card_info(code)
    basePower = card_info['power']
    return basePower

def get_character_power(player, character):
    basePower = get_character_base_power(character)
    donPower = get_don_power(player, character)
    power_manipulation_turn = character['powerManipulationTurn']
    power = basePower + donPower + power_manipulation_turn
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

def get_deck(player):
    return game[player]['deck']

def set_winner(player):
    game['winner'] = player

def has_winner():
    return game['winner'] is not None

def is_exhausted(character):
    return character['isExhausted']

def _inject_state(state):
    game.clear()
    game.update(state)