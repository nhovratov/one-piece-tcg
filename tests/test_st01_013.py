import unittest
import optcg.state as state
import optcg.action as action
import optcg.calc as calc

class TestST01_013(unittest.TestCase):

    def test_effect_positive(self):
        statePlayer1 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['hand'] = ['ST01-013']
        game['player1']['field']['don']['active'] = 4
        state._inject_state(game)

        action.perform_move('player1', 'c:0')
        action.perform_move('player1', 'g:0:1')

        zoro = state.get_character('player1', 0)

        self.assertEqual(7000, calc.get_character_power('player1', zoro))

    def test_effect_opponents_turn(self):
        statePlayer1 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'turn': 3,
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['hand'] = ['ST01-013']
        game['player1']['field']['don']['active'] = 4
        state._inject_state(game)

        action.perform_move('player1', 'c:0')
        action.perform_move('player1', 'g:0:1')

        action.next_turn()

        zoro = state.get_character('player1', 0)

        self.assertEqual(6000, calc.get_character_power('player1', zoro))

    def test_effect_negative(self):
        statePlayer1 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['hand'] = ['ST01-013']
        game['player1']['field']['don']['active'] = 4
        state._inject_state(game)

        action.perform_move('player1', 'c:0')

        zoro = state.get_character('player1', 0)

        self.assertEqual(5000, calc.get_character_power('player1', zoro))

if __name__ == '__main__':
    unittest.main()