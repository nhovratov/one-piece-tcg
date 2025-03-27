import unittest
import optcg.state as state
from optcg.state import game

class TestStringMethods(unittest.TestCase):

    def test_create(self):
        deck1 = {
            'leader': 'OP01-001',
            'deck': [
                'OP02-034',
                'OP02-033',
                'OP02-043',
            ],
        }
        deck2 = {
            'leader': 'ST11-001',
            'deck': [
                'OP02-034',
                'EB01-017',
                'OP02-033',
            ],
        }

        state.create(deck1, deck2)
        
        self.assertEqual(game['player1']['leader'], 'OP01-001')
        self.assertEqual(game['player2']['leader'], 'ST11-001')
        self.assertEqual(game['player1']['deck'], deck1['deck'])
        self.assertEqual(game['player2']['deck'], deck2['deck'])

    def test_get_leader(self):
        game['player1'] = {
            'field': {
                'leader': 'OP01-001'
            }
        }
        
        self.assertEqual(state.get_leader('player1'), 'OP01-001')

    def test_get_life_count(self):
        game['player1'] = {
            'life': [
                {},
                {},
            ]
        }
        
        self.assertEqual(state.get_life_count('player1'), 2)

    def test_get_available_don(self):
        game['player1'] = {
            'field': {
                'don': {
                    'active': 2
                }
            }
        }

        self.assertEqual(state.get_available_don('player1'), 2)

if __name__ == '__main__':
    unittest.main()