import sys
import yaml
import optcg.deck as deck
import optcg.state as state
import optcg.ai as ai
import optcg.user as user
import optcg.view as view
import optcg.action as action
import optcg.log as log

print_log = True if len(sys.argv) > 1 and sys.argv[1] == 'print' else False
log.set_print_log(print_log)

with open('config.yaml') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
player1_conf = config['player1']
player2_conf = config['player2']

deck1 = deck.create(player1_conf['deck'])
deck2 = deck.create(player2_conf['deck'])
state.create(deck1, deck2)

if player1_conf['ai_strategy_attack'] == 'manual':
    ai.set_ai_move1(user.get_manual_move)
else:
    ai.set_ai_move1(getattr(ai, player1_conf['ai_strategy_attack']))

if player1_conf['ai_strategy_counter'] == 'manual':
    ai.set_ai_counter_move1(user.manual_counter)
else:
    ai.set_ai_counter_move1(getattr(ai, player1_conf['ai_strategy_counter']))

ai.set_ai_move2(getattr(ai, player2_conf['ai_strategy_attack']))
ai.set_ai_counter_move2(getattr(ai, player2_conf['ai_strategy_counter']))
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
    if state.has_winner():
        break
    view.printBoard('player1')