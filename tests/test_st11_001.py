import unittest
import optcg.state as state
import optcg.action as action

class TestST11_001(unittest.TestCase):

    def test_st11_001_effect_positive(self):
        game = {
            'playerTurn': 'player1',
            'player1': {
                'deck': [
                    'ST11-002',
                ],
                'leader': 'ST11-001',
                'field': {
                    'leader': {
                        'code': 'ST11-001',
                        'status': 'active',
                        'powerIncreaseBattle': 0,
                        'attachedDon': 1,
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
            },
            'player2': {
                'deck': [],
                'leader': 'ST11-001',
                'field': {
                    'leader': {
                        'code': 'ST11-001',
                        'status': 'active',
                        'powerIncreaseBattle': 0,
                        'attachedDon': 1,
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
        }
        state._inject_state(game)

        action.perform_move('player1', 'b:l:l')

        hand = state.get_hand('player1')
        self.assertEqual(len(hand), 1)
        self.assertEqual(hand[0], 'ST11-002')

    def test_st11_001_effect_negative(self):
        game = {
            'playerTurn': 'player1',
            'player1': {
                'deck': [
                    'OP01-024',
                ],
                'leader': 'ST11-001',
                'field': {
                    'leader': {
                        'code': 'ST11-001',
                        'status': 'active',
                        'powerIncreaseBattle': 0,
                        'attachedDon': 1,
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
            },
            'player2': {
                'deck': [],
                'leader': 'ST11-001',
                'field': {
                    'leader': {
                        'code': 'ST11-001',
                        'status': 'active',
                        'powerIncreaseBattle': 0,
                        'attachedDon': 1,
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
        }
        state._inject_state(game)

        action.perform_move('player1', 'b:l:l')

        deck = state.get_deck('player1')
        self.assertEqual(deck[0], 'OP01-024')

    def test_st11_001_effect_once_per_turn(self):
        game = {
            'playerTurn': 'player1',
            'player1': {
                'deck': [
                    'ST11-002',
                    'ST11-002',
                ],
                'leader': 'ST11-001',
                'field': {
                    'leader': {
                        'code': 'ST11-001',
                        'status': 'active',
                        'powerIncreaseBattle': 0,
                        'attachedDon': 1,
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
            },
            'player2': {
                'deck': [],
                'leader': 'ST11-001',
                'field': {
                    'leader': {
                        'code': 'ST11-001',
                        'status': 'active',
                        'powerIncreaseBattle': 0,
                        'attachedDon': 1,
                    },
                    'stage': {},
                    'characters': [],
                    'don': {'active': 0, 'rested': 0}
                },
                'hand': [],
                'trash': [],
                'life': [
                    'OP01-047',
                    'OP01-047',
                ],
                'don_deck': 10,
                'battleEffects': []
            }
        }
        state._inject_state(game)

        action.perform_move('player1', 'b:l:l')
        action.unrest_leader('player1')
        action.perform_move('player1', 'b:l:l')

        hand = state.get_hand('player1')
        self.assertEqual(len(hand), 1)
        self.assertEqual(hand[0], 'ST11-002')

    def test_st11_001_effect_once_per_turn_next_turn(self):
        game = {
            'playerTurn': 'player1',
            'player1': {
                'deck': [
                    'ST11-002',
                    'ST11-002',
                ],
                'leader': 'ST11-001',
                'field': {
                    'leader': {
                        'code': 'ST11-001',
                        'status': 'active',
                        'powerIncreaseBattle': 0,
                        'attachedDon': 1,
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
            },
            'player2': {
                'deck': [],
                'leader': 'ST11-001',
                'field': {
                    'leader': {
                        'code': 'ST11-001',
                        'status': 'active',
                        'powerIncreaseBattle': 0,
                        'attachedDon': 1,
                    },
                    'stage': {},
                    'characters': [],
                    'don': {'active': 0, 'rested': 0}
                },
                'hand': [],
                'trash': [],
                'life': [
                    'OP01-047',
                    'OP01-047',
                ],
                'don_deck': 10,
                'battleEffects': []
            }
        }
        state._inject_state(game)

        action.perform_move('player1', 'b:l:l')
        action.unrest_leader('player1')
        action.reset_effect_restrictions('player1')
        action.perform_move('player1', 'b:l:l')

        hand = state.get_hand('player1')
        self.assertEqual(len(hand), 2)
        self.assertEqual(hand[0], 'ST11-002')
        self.assertEqual(hand[1], 'ST11-002')

if __name__ == '__main__':
    unittest.main()