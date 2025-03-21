import sys
import optcg.deck as deck
import optcg.state as state
import optcg.ai as ai
import optcg.view as view
import optcg.action as action
import optcg.log as log

print_log = True if len(sys.argv) > 1 and sys.argv[1] == 'print' else False
log.set_print_log(print_log)

deck1 = deck.create('deck1')
deck2 = deck.create('deck2')
state.create(deck1, deck2)
ai.set_ai_move1(ai.ai_move_aggro)
ai.set_ai_move2(ai.ai_move_control)
ai.set_ai_counter_move1(ai.ai_counter_early_characters)
ai.set_ai_counter_move2(ai.ai_counter_early_characters)
action.set_player1_move(ai.ai_move1)
action.set_player2_move(ai.ai_move2)

action.shuffle_deck('player1')
action.shuffle_deck('player2')
action.draw_cards('player1', 5)
action.draw_cards('player2', 5)
action.init_life('player1')
action.init_life('player2')

while True:
    action.next_turn()
    action.player_action()
    view.printBoard('player1')