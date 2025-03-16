def create_state(deck1, deck2):
    return {
        'turn': 0,
        'playerTurn': None,
        'player1': create_player_state(deck1),
        'player2': create_player_state(deck2),
    }


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
