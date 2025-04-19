import unittest
import optcg.state as state
import optcg.action as action

class TestST01_004(unittest.TestCase):

    def test_effect_positive(self):
        game = {
            'playerTurn': 'player1',
            'player1': {
                'deck': [],
                'leader': 'ST01-001',
                'field': {
                    'leader': {
                        'code': 'ST01-001',
                        'status': 'active',
                        'powerIncreaseBattle': 0,
                        'attachedDon': 0,
                    },
                    'stage': {},
                    'characters': [],
                    'don': {'active': 4, 'rested': 1}
                },
                'hand': ['ST01-004'],
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

        action.perform_move('player1', 'c:0')
        action.perform_move('player1', 'g:0:2')
        sanji = state.get_character('player1', 0)

        self.assertFalse(state.is_exhausted(sanji))

if __name__ == '__main__':
    unittest.main()