import unittest
import optcg.state as state
import optcg.action as action

class TestST01_004(unittest.TestCase):

    def test_effect_positive(self):
        statePlayer1 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['field']['don']['active'] = 4
        game['player1']['hand'] = ['ST01-004']
        state._inject_state(game)

        action.perform_move('player1', 'c:0')
        action.perform_move('player1', 'g:0:2')
        sanji = state.get_character('player1', 0)

        self.assertFalse(state.is_exhausted(sanji))

if __name__ == '__main__':
    unittest.main()