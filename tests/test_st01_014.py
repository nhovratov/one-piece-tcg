import unittest
import optcg.state as state
import optcg.action as action
import optcg.calc as calc

class TestST01_014(unittest.TestCase):

    def test_effect_positive(self):
        statePlayer1 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        statePlayer2 = state.create_player_state({'deck': [], 'leader': 'ST01-001'})
        game = {
            'playerTurn': 'player1',
            'player1': statePlayer1,
            'player2': statePlayer2
        }
        game['player1']['life'] = ['ST01-014']
        state._inject_state(game)

        action.dealDamage('player1')

        leader_power = state.get_leader_power('player1')
        self.assertEqual(6000, leader_power)
        self.assertEqual([], state.get_hand('player1'))
        self.assertEqual(['ST01-014'], state.get_trash('player1'))

if __name__ == '__main__':
    unittest.main()