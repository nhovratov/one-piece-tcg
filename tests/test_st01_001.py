import unittest
import optcg.state as state
import optcg.action as action

class TestST01_001(unittest.TestCase):

    def test_effect_positive(self):
        statePlayer1 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['field']['don']['rested'] = 1
        state._inject_state(game)

        action.perform_move('player1', 'a:l l')

        leader = state.get_leader('player1')
        don = state.get_attached_don(leader)
        rested_don = state.get_rested_don('player1')

        self.assertEqual(don, 1)
        self.assertEqual(rested_don, 0)

if __name__ == '__main__':
    unittest.main()