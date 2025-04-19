import unittest
import optcg.state as state
import optcg.action as action

class TestST01_005(unittest.TestCase):

    def test_effect_positive(self):
        statePlayer1 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['field']['don']['active'] = 10
        game['player1']['hand'] = ['ST01-005', 'ST01-004']
        state._inject_state(game)

        # Play Jinbe
        action.perform_move('player1', 'c:0')
        # Play Sanji
        action.perform_move('player1', 'c:0')
        # Give Jinbe 1 DON
        action.perform_move('player1', 'g:0:1')
        # Attack with Jinbe and choose Sanji for effect target
        jinbe = state.get_character('player1', 0)
        action.rush_character(jinbe)
        action.perform_move('player1', 'b:0:l 1')

        sanji = state.get_character('player1', 1)
        self.assertEqual(5000, state.get_character_power('player1', sanji))

if __name__ == '__main__':
    unittest.main()