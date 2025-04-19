import random
from optcg.log import log
import optcg.info as info
import optcg.state as state
import optcg.rule as rule
import optcg.util as util
import optcg.effect as effect
import optcg.ai as ai
import optcg.view as view
import optcg.action as action
import optcg.calc as calc
from optcg.state import game

player1_move = None
player2_move = None

def set_player1_move(move):
    global player1_move
    player1_move = move

def set_player2_move(move):
    global player2_move
    player2_move = move

def player_action():
    player = game['playerTurn']
    while True:
        if state.has_winner():
            break
        if player == 'player1':
            move = ai.ai_move1(player)
        else:
            move = ai.ai_move2(player)
        result = perform_move(player, move)
        if not result:
            break

def perform_move(player, move):
    parts = move.split(' ')
    arguments = parts[0].split(':')
    chosen_action = arguments[0]
    if chosen_action == 'e':
        return False
    elif chosen_action == 'c':
        characterIndexToTrash = None
        if len(arguments) == 3:
            characterIndexToTrash = int(arguments[2])
        action.play_card(player, int(arguments[1]), characterIndexToTrash)
    elif chosen_action == 'b':
        action.battle(player, arguments[1], arguments[2])
    elif chosen_action == 'g':
        action.attach_don(player, arguments[1], int(arguments[2]))
    elif chosen_action == 'a':
        if arguments[1] == 'l':
            character_or_leader = state.get_leader(player)
        else:
            character_or_leader = state.get_character(player)
        if effect.can_be_activated(player, character_or_leader):
            log('Effect of ' + character_or_leader['code'] + ' is activated')
            effect.resolve_effect(player, character_or_leader, parts[1:])
        else:
            log('Effect can not be activated')
    return True

def shuffle_deck(player):
    random.shuffle(game[player]['deck'])

def draw_cards(player, number):
    log(player + ' draws ' + str(number) + ' card')
    game[player]['hand'] += game[player]['deck'][:number]
    game[player]['deck'] = game[player]['deck'][number:]

def addCardToHand(player, card):
    log('Card ' + info.getHumanReadableCharacterName(card) + ' added to hand')
    game[player]['hand'].append(card)

def revealCards(player, number):
    cards = game[player]['deck'][:number]
    game[player]['deck'] = game[player]['deck'][number:]
    for card in cards:
        log('Card ' + info.getHumanReadableCharacterName(card) + ' revealed')
    return cards

def bottom_deck(player, cards):
    game[player]['deck'] = cards + game[player]['deck']

def draw_don(player, number):
    don_deck_number = game[player]['don_deck']
    if don_deck_number == 0:
        return
    if don_deck_number < number:
        number = don_deck_number
    log(player + ' draws ' + str(number) + ' DON!!')
    game[player]['don_deck'] -= number
    game[player]['field']['don']['active'] += number
    log(player + ' now has ' + str(game[player]['field']['don']['active']) + ' DON!!')

def init_life(player):
    leader = state.get_leader(player)
    leader_info = info.get_card_info(leader['code'])
    number = leader_info['life']
    game[player]['life'] = game[player]['deck'][:number]
    game[player]['deck'] = game[player]['deck'][number:]

def rest_don(player, number):
    game[player]['field']['don']['rested'] += number
    game[player]['field']['don']['active'] -= number

def unrest_all_don(player):
    game[player]['field']['don']['active'] += game[player]['field']['don']['rested']
    game[player]['field']['don']['rested'] = 0

def return_all_attached_don(player):
    leader = state.get_leader(player)
    return_attached_don(player, leader)
    for character in game[player]['field']['characters']:
        return_attached_don(player, character)

def return_attached_don(player, character):
    game[player]['field']['don']['active'] += state.get_attached_don(character)
    character['attachedDon'] = 0

def attach_don(player, index, number):
    numberActiveDon = state.get_available_don(player)
    if number > numberActiveDon:
        number = numberActiveDon
    game[player]['field']['don']['active'] -= number
    characterOrLeader = None
    if index == 'l':
        characterOrLeader = state.get_leader(player)
    else:
        characterOrLeader = state.get_character(player, int(index))
    characterOrLeader['attachedDon'] += number
    cardCode = characterOrLeader['code']
    effect.resolve_when_attaching_don(player, characterOrLeader)
    log(player + ' attaches ' + str(number) + ' DON!! to ' + info.getHumanReadableCharacterName(cardCode))

def attach_rested_don(player, index, number):
    number_rested_don = state.get_rested_don(player)
    if number > number_rested_don:
        number = number_rested_don
    game[player]['field']['don']['rested'] -= number
    if index == 'l':
        game[player]['field']['leader']['attachedDon'] += number
        cardCode = state.get_leader(player)['code']
    else:
        game[player]['field']['characters'][int(index)]['attachedDon'] += number
        cardCode = state.get_character(player, int(index))['code']
    log(player + ' attaches ' + str(number) + ' rested DON!! to ' + info.getHumanReadableCharacterName(cardCode))

def unrest_characters(player):
    for character in game[player]['field']['characters']:
        character['status'] = 'active'
        rush_character(character)

def rush_character(character):
    character['isExhausted'] = False

def rest_character(player, index):
    game[player]['field']['characters'][index]['status'] = 'rested'

def rest_leader(player):
    game[player]['field']['leader']['status'] = 'rested'

def unrest_leader(player):
    game[player]['field']['leader']['status'] = 'active'

def reset_board(player):
    unrest_all_don(player)
    return_all_attached_don(player)
    unrest_characters(player)
    unrest_leader(player)
    reset_effect_restrictions(player)

def reset_effect_restrictions(player):
    for character in game[player]['field']['characters']:
        effect_used_this_turn = character.get('effect_used_this_turn')
        if effect_used_this_turn:
            character['effect_used_this_turn'] = False
    leader = state.get_leader(player)
    effect_used_this_turn = leader.get('effect_used_this_turn')
    if effect_used_this_turn:
        leader['effect_used_this_turn'] = False

def trash_character(player, index):
    character = state.get_character(player, index)
    card = character['code']
    # Return attached DON!!
    return_attached_don(player, character)
    game[player]['trash'].append(card)
    game[player]['field']['characters'].pop(index)
    log(player + ' trashes character: ' + info.getHumanReadableCharacterName(card))

def trash_card(player, index):
    hand = state.get_hand(player)
    card = hand[index]
    game[player]['trash'].append(card)
    game[player]['hand'].pop(index)
    log(player + ' trashes ' + info.getHumanReadableCharacterName(card))

def next_turn():
    game['turn'] += 1
    turn = state.get_game_turn()
    if game['playerTurn'] is None:
        game['playerTurn'] = random.choice(['player1', 'player2'])
    elif game['playerTurn'] == 'player1':
        game['playerTurn'] = 'player2'
    else:
        game['playerTurn'] = 'player1'
    playerTurn = game['playerTurn']
    log('Turn: ' + str(turn))
    log('Player: ' + playerTurn)
    reset_board(playerTurn)
    if turn == 1:
        draw_don(playerTurn, 1)
    else:
        draw_cards(playerTurn, 1)
        draw_don(playerTurn, 2)

def play_card(player, index, trashCharacterIndex = None):
    card = state.get_hand(player)[index]
    cardInfo = info.get_card_info(card)
    isExhausted = info.hasRush(card) == False
    cost = cardInfo['cost']
    if not rule.can_play_card(player, index):
        raise Exception('Can not play card')
    numberOfCharacters = state.get_number_of_player_characters(player)
    if numberOfCharacters == 5 and trashCharacterIndex is None:
        raise Exception('Index for trashing character on the field must be defined')
    rest_don(player, cost)
    game[player]['hand'].pop(index)
    character = {'code': card, 'status': 'active', 'isExhausted': isExhausted, 'powerIncreaseBattle': 0, 'attachedDon': 0}
    if numberOfCharacters == 5:
        trash_character(player, trashCharacterIndex)
    game[player]['field']['characters'].append(character)
    log(player + ' plays ' + cardInfo['name'] + ' [' + card + '] for ' + str(cardInfo['cost']) + ' DON!!')

def counter_attack_leader(player, counterIndex):
    card = state.get_hand(player)[counterIndex]
    cardInfo = info.get_card_info(card)
    counter = cardInfo['counter']
    increaseBattlePowerOfLeader(player, counter)
    trash_card(player, counterIndex)

def counter_attack_character(player, counterIndex, characterIndex):
    card = state.get_hand(player)[counterIndex]
    cardInfo = info.get_card_info(card)
    counter = cardInfo['counter']
    increaseBattlePowerOfCharacter(player, counter, characterIndex)
    trash_card(player, counterIndex)

def increaseBattlePowerOfLeader(player, counter):
    game[player]['field']['leader']['powerIncreaseBattle'] += counter

def increaseBattlePowerOfCharacter(player, counter, characterIndex):
    game[player]['field']['characters'][characterIndex]['powerIncreaseBattle'] += counter

def battle(player, attackingCharacterIndexOrLeader, attackTargetIndexOrLeader):
    attackerIsLeader = attackingCharacterIndexOrLeader == 'l'
    targetIsLeader = attackTargetIndexOrLeader == 'l'
    if not attackerIsLeader:
        attackingCharacterIndexOrLeader = int(attackingCharacterIndexOrLeader)
    if not targetIsLeader:
        attackTargetIndexOrLeader = int(attackTargetIndexOrLeader)
    if not attackerIsLeader and not rule.can_attack_with_character(player, attackingCharacterIndexOrLeader):
        return
    if not targetIsLeader and not rule.can_attack_character(player, attackTargetIndexOrLeader):
        return
    if attackerIsLeader and not rule.can_attack_with_leader(player):
        return
    if attackerIsLeader:
        rest_leader(player)
        attackingCharacterOrLeader = state.get_leader(player)
    else:
        rest_character(player, attackingCharacterIndexOrLeader)
        attackingCharacterOrLeader = state.get_character(player, attackingCharacterIndexOrLeader)
    opponent = util.getOpponent(player)
    target_characterOrLeader = state.get_leader(opponent) if targetIsLeader else state.get_character(opponent, attackTargetIndexOrLeader)
    targetInfo = info.get_card_info(target_characterOrLeader['code'])
    attackerInfo = info.get_card_info(attackingCharacterOrLeader['code'])

    log('Attacking: '
    + attackerInfo['name']
    + ' [' + attackingCharacterOrLeader['code'] + ']'
    + ' declares attack on '
    + targetInfo['name']
    + ' [' + targetInfo['code'] + ']')

    effect.resolveWhenAttackingEffect(player, attackingCharacterOrLeader)
    attackerPower = calc.get_character_power(player, attackingCharacterOrLeader)

    if rule.canBlock(opponent) and attackerPower > 6000:
        blockerIndex = getBlocker(opponent)
        if blockerIndex is not None:
            attackTargetIndexOrLeader = blockerIndex
            target_characterOrLeader = state.get_character(opponent, blockerIndex)
            code = target_characterOrLeader['code']
            targetInfo = info.get_card_info(code)
            targetIsLeader = False
            rest_character(opponent, blockerIndex)
            log('Opponent blocks with ' + info.getHumanReadableCharacterName(code))

    targetPower = targetInfo['power']
    while True:
        if not rule.can_counter(opponent):
            break
        targetBattlePower = targetPower + target_characterOrLeader['powerIncreaseBattle']
        if opponent == 'player1':
            counter = ai.ai_counter1(opponent, attackerPower, targetBattlePower, targetInfo)
        else:
            counter = ai.ai_counter2(opponent, attackerPower, targetBattlePower, targetInfo)
        if counter == 'e':
            break

        if not state.hand_card_exists_at_index(opponent, counter):
            continue
        card = state.get_hand(opponent)[counter]
        if targetIsLeader:
            counter_attack_leader(opponent, counter)
        else:
            counter_attack_character(opponent, counter, attackTargetIndexOrLeader)
    targetPower += target_characterOrLeader['powerIncreaseBattle']

    log('Battle: '
    + attackerInfo['name']
    + ' [' + attackingCharacterOrLeader['code'] + ']'
    + ' (' + str(attackerPower) + ')'
    + ' attacks '
    + targetInfo['name']
    + ' [' + targetInfo['code'] + '] (' + str(targetPower) + ')')

    if targetPower <= attackerPower:
        if targetIsLeader:
            log('Turn player deals one damage')
            dealDamage(opponent)
            if state.has_winner():
                return
        else:
            log('Opponent\'s character ' + info.getHumanReadableCharacterName(targetInfo['code']) + ' is K.O.\'ed')
            trash_character(opponent, attackTargetIndexOrLeader)
    else:
        log('Opponent counters the attack')
    target_characterOrLeader['powerIncreaseBattle'] = 0
    game['player1']['battleEffects'] = []
    game['player2']['battleEffects'] = []


def getBlocker(player):
    ignoreBlockerEffect = None
    for effect in game[player]['battleEffects']:
        if effect['type'] == 'ignoreBlocker':
            ignoreBlockerEffect = effect
            break
    characterList = state.get_characters(player)
    for (index, character) in enumerate(characterList):
        if state.isCharacterRested(player, index):
            continue
        if info.hasBlocker(character['code']):
            if ignoreBlockerEffect is not None:
                characterPower = calc.get_character_power(player, character)
                effectPower = ignoreBlockerEffect['power']
                if ignoreBlockerEffect['comparison'] == 'lessThanOrEqual':
                    if characterPower <= effectPower:
                        continue
            return index
    return None

def dealDamage(opponent):
    if len(game[opponent]['life']) == 0:
        player = util.getOpponent(opponent)
        view.printBoard('player1')
        leaderName = info.getHumanReadableCharacterName(state.get_leader(player)['code'])
        print(leaderName + ' (' + player + ') wins')
        state.set_winner(player)
        return
    card = game[opponent]['life'][-1:]
    game[opponent]['hand'] += card
    game[opponent]['life'] = game[opponent]['life'][:-1]