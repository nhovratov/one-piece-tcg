import unittest
import optcg.state as state
import optcg.action as action

class TestST11_001(unittest.TestCase):

    def test_st11_001_effect_positive(self):
        statePlayer1 = state.create_player_state({'deck': ['ST11-002'], 'leader': 'ST11-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['field']['don']['active'] = 1

        state._inject_state(game)

        action.perform_move('player1', 'g:l:1')
        action.perform_move('player1', 'b:l:l')

        hand = state.get_hand('player1')
        self.assertEqual(len(hand), 1)
        self.assertEqual(hand[0], 'ST11-002')

    def test_st11_001_effect_negative(self):
        statePlayer1 = state.create_player_state({'deck': ['OP01-024'], 'leader': 'ST11-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['field']['don']['active'] = 1
        state._inject_state(game)

        action.perform_move('player1', 'g:l:1')
        action.perform_move('player1', 'b:l:l')

        deck = state.get_deck('player1')
        self.assertEqual(deck[0], 'OP01-024')

    def test_st11_001_effect_once_per_turn(self):
        statePlayer1 = state.create_player_state({'deck': ['ST11-002', 'ST11-002'], 'leader': 'ST11-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['field']['don']['active'] = 1
        state._inject_state(game)

        action.perform_move('player1', 'g:l:1')
        action.perform_move('player1', 'b:l:l')
        action.unrest_leader('player1')
        action.perform_move('player1', 'b:l:l')

        hand = state.get_hand('player1')
        self.assertEqual(len(hand), 1)
        self.assertEqual(hand[0], 'ST11-002')

    def test_st11_001_effect_once_per_turn_next_turn(self):
        statePlayer1 = state.create_player_state({'deck': ['ST11-002', 'ST11-002'], 'leader': 'ST11-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['field']['don']['active'] = 1
        state._inject_state(game)

        action.perform_move('player1', 'g:l:1')
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