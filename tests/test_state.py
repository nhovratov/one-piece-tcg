import unittest
import optcg.state
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

        optcg.state.create(deck1, deck2)
        
        self.assertEqual(game['player1']['leader'], 'OP01-001')
        self.assertEqual(game['player2']['leader'], 'ST11-001')
        self.assertEqual(game['player1']['deck'], deck1['deck'])
        self.assertEqual(game['player2']['deck'], deck2['deck'])

if __name__ == '__main__':
    unittest.main()