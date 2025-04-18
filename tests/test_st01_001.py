import unittest
import optcg.state as state
import optcg.action as action

class TestST01_001(unittest.TestCase):

    def test_st11_001_effect_positive(self):
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
                    'don': {'active': 0, 'rested': 1}
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

        action.perform_move('player1', 'a:l l')

        leader = state.get_leader('player1')
        don = state.get_attached_don(leader)
        rested_don = state.get_rested_don('player1')

        self.assertEqual(don, 1)
        self.assertEqual(rested_don, 0)

if __name__ == '__main__':
    unittest.main()