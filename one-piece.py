import sys
import json
import random
import pprint
from tabulate import tabulate
from time import sleep
import math
import game.deck as deck

PLAYER1 = 'player1'
PLAYER2 = 'player2'
PRINT_LOG = True if len(sys.argv) > 1 and sys.argv[1] == 'print' else False

with open('card-db.json', 'r') as file:
    cardDatabase = json.load(file)

def log(message):
    if PRINT_LOG:
        print(message)

def shuffle_deck(player):
    random.shuffle(game[player]['deck'])

def draw_cards(player, number):
    log(player + ' draws ' + str(number) + ' card')
    game[player]['hand'] += game[player]['deck'][:number]
    game[player]['deck'] = game[player]['deck'][number:]

def addCardToHand(player, card):
    log('Card ' + getHumanReadableCharacterName(card) + ' added to hand')
    game[player]['hand'].append(card)

def revealCards(player, number):
    cards = game[player]['deck'][:number]
    game[player]['deck'] = game[player]['deck'][number:]
    for card in cards:
        log('Card ' + getHumanReadableCharacterName(card) + ' revealed')
    return cards

def bottomDeck(player, cards):
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
    leader = game[player]['leader']
    number = cardDatabase[leader]['life']
    game[player]['life'] = game[player]['deck'][:number]
    game[player]['deck'] = game[player]['deck'][number:]

def rest_don(player, number):
    game[player]['field']['don']['rested'] += number
    game[player]['field']['don']['active'] -= number

def unrest_all_don(player):
    game[player]['field']['don']['active'] += game[player]['field']['don']['rested']
    game[player]['field']['don']['rested'] = 0

def return_all_attached_don(player):
    leader = get_leader(player)
    return_attached_don(player, leader)
    for character in game[player]['field']['characters']:
        return_attached_don(player, character)

def return_attached_don(player, character):
    game[player]['field']['don']['active'] += getAttachedDon(character)
    character['attachedDon'] = 0

def attach_don(player, index, number):
    numberActiveDon = getAvailableDon(player)
    if number > numberActiveDon:
        number = numberActiveDon
    game[player]['field']['don']['active'] -= number
    if index == 'l':
        game[player]['field']['leader']['attachedDon'] += number
        cardCode = get_leader(player)['code']
    else:
        game[player]['field']['characters'][int(index)]['attachedDon'] += number
        cardCode = get_character(player, int(index))['code']
    log(player + ' attaches ' + str(number) + ' DON!! to ' + getHumanReadableCharacterName(cardCode))

def unrest_characters(player):
    for index, character in enumerate(game[player]['field']['characters']):
        game[player]['field']['characters'][index]['status'] = 'active'
        game[player]['field']['characters'][index]['isExhausted'] = False

def rest_character(player, index):
    game[player]['field']['characters'][index]['status'] = 'rested'

def isCharacterRested(player, index):
    return game[player]['field']['characters'][index]['status'] == 'rested'

def rest_leader(player):
    game[player]['field']['leader']['status'] = 'rested'

def unrest_leader(player):
    game[player]['field']['leader']['status'] = 'active'

def trash_character(player, index):
    character = get_character(player, index)
    card = character['code']
    # Return attached DON!!
    return_attached_don(player, character)
    game[player]['trash'].append(card)
    game[player]['field']['characters'].pop(index)
    log(player + ' trashes character: ' + getHumanReadableCharacterName(card))

def trash_card(player, index):
    hand = get_hand(player)
    card = hand[index]
    game[player]['trash'].append(card)
    game[player]['hand'].pop(index)
    log(player + ' trashes ' + getHumanReadableCharacterName(card))

def next_turn():
    game['turn'] += 1
    turn = get_game_turn()
    if game['playerTurn'] is None:
        game['playerTurn'] = random.choice([PLAYER1, PLAYER2])
    elif game['playerTurn'] == PLAYER1:
        game['playerTurn'] = PLAYER2
    else:
        game['playerTurn'] = PLAYER1
    playerTurn = game['playerTurn']
    log('Turn: ' + str(turn))
    log('Player: ' + playerTurn)
    unrest_all_don(playerTurn)
    return_all_attached_don(playerTurn)
    unrest_characters(playerTurn)
    unrest_leader(playerTurn)
    if turn == 1:
        draw_don(playerTurn, 1)
    else:
        draw_cards(playerTurn, 1)
        draw_don(playerTurn, 2)

def get_game_turn():
    return game['turn']

def player_is_allowed_to_attack():
    turn = get_game_turn()
    return turn > 2

def get_turn_player():
    return game['playerTurn']

def get_don_deck(player):
    return game[player]['don_deck']

def get_overall_don(player):
    return 10 - get_don_deck(player)

def get_card_info(card):
    return cardDatabase[card]

def character_exists_at_index(player, index):
    return index < len(get_characterList(player))

def get_character(player, index):
    return get_characterList(player)[index]

def get_characterList(player):
    return game[player]['field']['characters']

def hand_card_exists_at_index(player, index):
    return index < len(get_hand(player))

def get_hand(player):
    return game[player]['hand']

def get_card(player, index):
    return game[player]['hand'][index]

def get_number_of_cards_in_hand(player):
    return len(get_hand(player))

def get_leader(player):
    return game[player]['field']['leader']

def get_life_count(player):
    return len(game[player]['life'])

def getAvailableDon(player):
    return game[player]['field']['don']['active']

def getRestedDon(player):
    return game[player]['field']['don']['rested']

def hasRush(code):
    info = get_card_info(code)
    return info.get('hasRush', False)

def hasBlocker(code):
    info = get_card_info(code)
    return info.get('hasBlocker', False)

def getNumberOfPlayerCharacters(player):
    return len(game[player]['field']['characters'])

def getNumberOfActiveCharacters(player):
    activeCharacters = [character for character in game[player]['field']['characters'] if character['status'] == 'active']
    return len(activeCharacters)

def getNumberOfCharactersAbleToAttack(player):
    activeCharacters = []
    for character in game[player]['field']['characters']:
        if character['status'] == 'rested':
            continue
        if character['isExhausted']:
            continue
        activeCharacters.append(character)
    return len(activeCharacters)

def getOpponent(player):
    return PLAYER2 if player == PLAYER1 else PLAYER1

def getHumanReadableCharacterName(code):
    info = get_card_info(code)
    if info['type'] == 'character':
        name = '[' + code + '] ' + info['name'] + ' (' + str(info['cost']) + ')'
    else:
        name = '[' + code + '] ' + info['name']
    return name

def printAvailableDon(player):
    log('DON!!: ' + str(getAvailableDon(player)))

def printNumberOfCardsInHand(player):
    log('Number of cards in hand: ' + str(len(get_hand(player))))

def printStatus(player):
    log('')
    table = [[get_life_count(player), getAvailableDon(player), get_number_of_cards_in_hand(player)]]
    headers = ['Life', 'DON!!', 'Hand size']
    log(tabulate(table, headers=headers, tablefmt="grid", disable_numparse=True))

def printHand(player):
    log('')
    counter = 1
    table = []
    for card in get_hand(player):
        cardInfo = get_card_info(card)
        parts = [
            str(counter) + ':',
            '[' + card + ']',
            cardInfo['name'],
            '(' + str(cardInfo['cost']) + ')',
            cardInfo['power'],
            cardInfo['counter']
        ]
        table.append(parts)
        counter += 1
    log(tabulate(table, headers=['', 'Code', 'Name', 'Cost', 'Power', 'Counter'], disable_numparse=True))

def printLeader(player):
    log('')
    leader = get_leader(player)
    cardInfo = get_card_info(leader['code'])
    parts = [
        '[' + cardInfo['code'] + ']',
        cardInfo['name'],
        getCharacterPower(player, leader),
        '↑ (active)' if leader['status'] == 'active' else '→ (rested)',
    ]
    log(tabulate([parts], headers=['Leader', 'Name', 'Power', 'Status'], tablefmt="grid", disable_numparse=True))

def printCharacters(player):
    log('')
    counter = 1
    table = []
    for character in game[player]['field']['characters']:
        card = character['code']
        cardInfo = get_card_info(character['code'])
        parts = [
            str(counter) + ':',
            '[' + card + ']',
            cardInfo['name'],
            '(' + str(cardInfo['cost']) + ')',
            getCharacterPower(player, character),
            '↑ (active)' if character['status'] == 'active' else '→ (rested)',
            'Yes' if character['isExhausted'] else '',
        ]
        table.append(parts)
        counter += 1
    log(tabulate(table, headers=['', 'Code', 'Name', 'Cost', 'Power', 'Status', 'Exhausted'], tablefmt="grid", disable_numparse=True))

def printBoard(player):
    opponent = getOpponent(player)
    printStatus(opponent)
    printLeader(opponent)
    printCharacters(opponent)
    printPlayerBoard(player)

def printPlayerBoard(player):
    printCharacters(player)
    printLeader(player)
    printStatus(player)

def print_actions():
    print('')
    print('Play Card (c)')
    print('Give DON!! (g)')
    print('Battle (b)')
    print('End Turn (e)')

def can_play_card(player, index, reservedDon = 0):
    card = get_hand(player)[index]
    cardInfo = get_card_info(card)
    availableDon = getAvailableDon(player)
    availableDon -= reservedDon
    return cardInfo['cost'] <= availableDon

def play_card(player, index, trashCharacterIndex = None):
    card = get_hand(player)[index]
    cardInfo = get_card_info(card)
    isExhausted = hasRush(card) == False
    cost = cardInfo['cost']
    if not can_play_card(player, index):
        raise Exception('Can not play card')
    numberOfCharacters = getNumberOfPlayerCharacters(player)
    if numberOfCharacters == 5 and trashCharacterIndex is None:
        raise Exception('Index for trashing character on the field must be defined')
    rest_don(player, cost)
    game[player]['hand'].pop(index)
    character = {'code': card, 'status': 'active', 'isExhausted': isExhausted, 'powerIncreaseBattle': 0, 'attachedDon': 0}
    if numberOfCharacters == 5:
        characterToTrash = game[player]['field']['characters'][trashCharacterIndex]
        trash_character(player, trashCharacterIndex)
    game[player]['field']['characters'].append(character)
    log(player + ' plays ' + cardInfo['name'] + ' [' + card + '] for ' + str(cardInfo['cost']) + ' DON!!')

def can_attack_with_character(player, index):
    character = game[player]['field']['characters'][index]
    if character['status'] == 'rested' or character['isExhausted']:
        return False
    return True

def can_attack_with_leader(player):
    leader = get_leader(player)
    if leader['status'] == 'rested':
        return False
    return True

def can_attack_character(player, index):
    opponent = getOpponent(player)
    character = game[opponent]['field']['characters'][index]
    if character['status'] == 'active':
        return False
    return True

def can_counter(player):
    hand = get_hand(player)
    for card in hand:
        cardInfo = get_card_info(card)
        if cardInfo['type'] == 'character' and cardInfo['counter'] > 0:
            return True
    return False

def counter_attack_leader(player, counterIndex):
    card = get_hand(player)[counterIndex]
    cardInfo = get_card_info(card)
    counter = cardInfo['counter']
    increaseBattlePowerOfLeader(player, counter)
    trash_card(player, counterIndex)

def counter_attack_character(player, counterIndex, characterIndex):
    card = get_hand(player)[counterIndex]
    cardInfo = get_card_info(card)
    counter = cardInfo['counter']
    increaseBattlePowerOfCharacter(player, counter, characterIndex)
    trash_card(player, counterIndex)

def increaseBattlePowerOfLeader(player, counter):
    game[player]['field']['leader']['powerIncreaseBattle'] += counter

def increaseBattlePowerOfCharacter(player, counter, characterIndex):
    game[player]['field']['characters'][characterIndex]['powerIncreaseBattle'] += counter

def getDonPower(player, character):
    return getAttachedDon(character) * 1000 if player == get_turn_player() else 0

def getAttachedDon(character):
    return character['attachedDon']

def getCharacterPower(player, character):
    code = character['code']
    info = get_card_info(code)
    basePower = info['power']
    donPower = getDonPower(player, character)
    power = basePower + donPower
    power += checkPermanentCharacterPowerEffects(player, character)
    return power

def getLeaderPower(player):
    leader = get_leader(player)
    return getCharacterPower(player, leader)

def battle(player, attackingCharacterIndexOrLeader, attackTargetIndexOrLeader):
    attackerIsLeader = attackingCharacterIndexOrLeader == 'l'
    targetIsLeader = attackTargetIndexOrLeader == 'l'
    if not attackerIsLeader:
        attackingCharacterIndexOrLeader = int(attackingCharacterIndexOrLeader)
    if not targetIsLeader:
        attackTargetIndexOrLeader = int(attackTargetIndexOrLeader)
    if not attackerIsLeader and not can_attack_with_character(player, attackingCharacterIndexOrLeader):
        return
    if not targetIsLeader and not can_attack_character(player, attackTargetIndexOrLeader):
        return
    if attackerIsLeader and not can_attack_with_leader(player):
        return
    if attackerIsLeader:
        rest_leader(player)
        attackingCharacterOrLeader = get_leader(player)
    else:
        rest_character(player, attackingCharacterIndexOrLeader)
        attackingCharacterOrLeader = get_character(player, attackingCharacterIndexOrLeader)
    opponent = getOpponent(player)
    target_characterOrLeader = get_leader(opponent) if targetIsLeader else get_character(opponent, attackTargetIndexOrLeader)
    targetInfo = get_card_info(target_characterOrLeader['code'])
    attackerInfo = get_card_info(attackingCharacterOrLeader['code'])

    log('Attacking: '
    + attackerInfo['name']
    + ' [' + attackingCharacterOrLeader['code'] + ']'
    + ' declares attack on '
    + targetInfo['name']
    + ' [' + targetInfo['code'] + ']')

    resolveWhenAttackingEffect(player, attackingCharacterOrLeader)
    attackerPower = getCharacterPower(player, attackingCharacterOrLeader)

    if canBlock(opponent) and attackerPower > 6000:
        blockerIndex = getBlocker(opponent)
        if blockerIndex is not None:
            attackTargetIndexOrLeader = blockerIndex
            target_characterOrLeader = get_character(opponent, blockerIndex)
            code = target_characterOrLeader['code']
            targetInfo = get_card_info(code)
            targetIsLeader = False
            rest_character(opponent, blockerIndex)
            log('Opponent blocks with ' + getHumanReadableCharacterName(code))

    targetPower = targetInfo['power']
    while True:
        if not can_counter(opponent):
            break
        targetBattlePower = targetPower + target_characterOrLeader['powerIncreaseBattle']
        if opponent == PLAYER1:
            counter = ai_counter1(opponent, attackerPower, targetBattlePower, targetInfo)
        else:
            counter = ai_counter2(opponent, attackerPower, targetBattlePower, targetInfo)
        if counter == 'e':
            break

        if not hand_card_exists_at_index(opponent, counter):
            continue
        card = get_hand(opponent)[counter]
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
        else:
            log('Opponent\'s character ' + getHumanReadableCharacterName(targetInfo['code']) + ' is K.O.\'ed')
            trash_character(opponent, attackTargetIndexOrLeader)
    else:
        log('Opponent counters the attack')
    target_characterOrLeader['powerIncreaseBattle'] = 0
    game[PLAYER1]['battleEffects'] = []
    game[PLAYER2]['battleEffects'] = []

def canBlock(player):
    ignoreBlockerEffect = None
    for effect in game[player]['battleEffects']:
        if effect['type'] == 'ignoreBlocker':
            ignoreBlockerEffect = effect
            break
    characterList = get_characterList(player)
    for (index, character) in enumerate(characterList):
        if isCharacterRested(player, index):
            continue
        if hasBlocker(character['code']):
            if ignoreBlockerEffect is not None:
                characterPower = getCharacterPower(player, character)
                effectPower = ignoreBlockerEffect['power']
                if ignoreBlockerEffect['comparison'] == 'lessThanOrEqual':
                    if characterPower <= effectPower:
                        continue
            return True
    return False

def getBlocker(player):
    ignoreBlockerEffect = None
    for effect in game[player]['battleEffects']:
        if effect['type'] == 'ignoreBlocker':
            ignoreBlockerEffect = effect
            break
    characterList = get_characterList(player)
    for (index, character) in enumerate(characterList):
        if isCharacterRested(player, index):
            continue
        if hasBlocker(character['code']):
            if ignoreBlockerEffect is not None:
                characterPower = getCharacterPower(player, character)
                effectPower = ignoreBlockerEffect['power']
                if ignoreBlockerEffect['comparison'] == 'lessThanOrEqual':
                    if characterPower <= effectPower:
                        continue
            return index
    return None

def dealDamage(opponent):
    if len(game[opponent]['life']) == 0:
        player = getOpponent(opponent)
        printBoard(PLAYER1)
        leaderName = getHumanReadableCharacterName(get_leader(player)['code'])
        print(leaderName + ' (' + player + ') wins')
        #print(player + ' wins on turn ' + str(get_game_turn()))
        exit()
    card = game[opponent]['life'][-1:]
    game[opponent]['hand'] += card
    game[opponent]['life'] = game[opponent]['life'][:-1]

def player_action():
    player = game['playerTurn']
    while True:
        if player == PLAYER1:
            move = ai_move1(player)
        else:
            move = ai_move2(player)
        arguments = move.split(':')
        action = arguments[0]
        if action == 'e':
            break
        elif action == 'c':
            characterIndexToTrash = None
            if len(arguments) == 3:
                characterIndexToTrash = int(arguments[2])
            play_card(player, int(arguments[1]), characterIndexToTrash)
        elif action == 'b':
            battle(player, arguments[1], arguments[2])
        elif action == 'g':
            attach_don(player, arguments[1], int(arguments[2]))

def ai_move_aggro(player):
    leaderMove = getLeaderMove(player)
    if leaderMove is not None:
        return leaderMove
    opponent = getOpponent(player)
    if canGoForLethal(player) or canGoForLethal(opponent):
        return goForLethal(player)
    availableDon = getAvailableDon(player)
    powerOpponentLeader = getLeaderPower(opponent)
    highestCostIndex = getHighestPlayableCostCharacterIndexInHand(player)
    highestCost = getHighestPlayableCostInHand(player)
    availableDonForBattle = availableDon - highestCost

    if not player_is_allowed_to_attack():
        return 'e'
    # Attack with characters:
    characterList = get_characterList(player)
    sortedCharacters = characterList.copy()
    sortedCharacters.sort(key=sortCharactersByPower)
    for character in sortedCharacters:
        index = characterList.index(character)
        if not can_attack_with_character(player, index):
            continue
        characterPower = getCharacterPower(player, character)
        if characterPower >= powerOpponentLeader:
            return 'b:' + str(index) + ':l'
        elif characterPower + (availableDonForBattle * 1000) >= powerOpponentLeader:
            return 'g:' + str(index) + ':' + str(int((powerOpponentLeader - characterPower) / 1000))
    # Full aggro: give remaining DON to leader
    if availableDonForBattle > 0:
        return 'g:l:' + str(availableDonForBattle)
    # Attack leader with leader
    if can_attack_with_leader(player):
        return 'b:l:l'
    # If there is enough DON to play a character, play that character.
    if highestCostIndex is not None:
        if getNumberOfPlayerCharacters(player) < 5:
            return 'c:' + str(highestCostIndex)
        # If board is full, check if there is something better to play.
        lowestCost = getLowestCost(player)
        lowestCostIndex = getLowestCostCharacterIndex(player)
        if highestCost > lowestCost:
            return 'c:' + str(highestCostIndex) + ':' + str(lowestCostIndex)
    return 'e'

def ai_move_control(player):
    leaderMove = getLeaderMove(player)
    if leaderMove is not None:
        return leaderMove
    opponent = getOpponent(player)
    if canGoForLethal(player) or canGoForLethal(opponent):
        return goForLethal(player)
    availableDon = getAvailableDon(player)
    powerLeader = getLeaderPower(player)
    powerOpponentLeader = getLeaderPower(opponent)
    # Prefer to play characters on curve
    highestBlockerCostIndex = None
    highestBlockerCost = 0
    highestCostIndex = getHighestPlayableCostCharacterIndexInHand(player, highestBlockerCost)
    highestCost = getHighestPlayableCostInHand(player, highestBlockerCost)
    if highestCost != availableDon:
        highestBlockerCostIndex = getHighestPlayableCostBlockerCharacterIndexInHand(player)
        highestBlockerCost = getHighestPlayableBlockerCostInHand(player)
        highestCostIndex = getHighestPlayableCostCharacterIndexInHand(player, highestBlockerCost)
        highestCost = getHighestPlayableCostInHand(player, highestBlockerCost)
    availableDonForBattle = availableDon - highestBlockerCost - highestCost

    if player_is_allowed_to_attack():
        # Find rested characters
        characterToAttack = 'l'
        powerOpponentCharacter = getLeaderPower(opponent)
        for (index, character) in enumerate(get_characterList(opponent)):
            if can_attack_character(player, index):
                characterToAttack = index
                powerOpponentCharacter = getCharacterPower(opponent, character)
                break
        # Attack with characters:
        for (index, character) in enumerate(get_characterList(player)):
            if not can_attack_with_character(player, index):
                continue
            if hasBlocker(character['code']):
                continue
            characterPower = getCharacterPower(player, character)
            if characterPower >= powerOpponentCharacter:
                return 'b:' + str(index) + ':' + str(characterToAttack)
            elif characterPower + (availableDonForBattle * 1000) >= powerOpponentCharacter:
                return 'g:' + str(index) + ':' + str(int((powerOpponentCharacter - characterPower) / 1000))
            elif characterPower >= powerOpponentLeader:
                return 'b:' + str(index) + ':l'
        # Full aggro: give remaining DON to leader
        if availableDonForBattle > 0:
            return 'g:l:' + str(availableDonForBattle)
        # Attack leader with leader
        if can_attack_with_leader(player):
            if powerOpponentCharacter > powerLeader:
                characterToAttack = 'l'
            return 'b:l:' + str(characterToAttack)

    # If there is enough DON to play a character, play that character.
    if highestBlockerCostIndex is not None:
        if getNumberOfPlayerCharacters(player) < 5:
            return 'c:' + str(highestBlockerCostIndex)
        # If board is full, check if there is something better to play.
        lowestCostIndex = getLowestCostCharacterIndex(player)
        lowestCost = getLowestCost(player)
        return 'c:' + str(highestBlockerCostIndex) + ':' + str(lowestCostIndex)
    if highestCostIndex is not None:
        if getNumberOfPlayerCharacters(player) < 5:
            return 'c:' + str(highestCostIndex)
        # If board is full, check if there is something better to play.
        lowestCostIndex = getLowestCostCharacterIndex(player)
        lowestCost = getLowestCost(player)
        if highestCost > lowestCost:
            return 'c:' + str(highestCostIndex) + ':' + str(lowestCostIndex)

    return 'e'

def ai_counter_mid(player, attackerPower, targetPower, target):
    # If life is less than 3, counter with all there is.
    counterNeeded = attackerPower - targetPower + 1000
    if counterNeeded <= 0:
        return 'e'
    maxCounter = 0
    for card in get_hand(player):
        cardInfo = get_card_info(card)
        if cardInfo['type'] == 'character' and cardInfo['counter'] > 0:
            maxCounter += cardInfo['counter']

    if counterNeeded == 1000:
        preferredCounter = 1000
    else:
        preferredCounter = 2000

    if get_life_count(player) < 3 and maxCounter >= counterNeeded:
        for (index, card) in enumerate(get_hand(player)):
            cardInfo = get_card_info(card)
            if cardInfo['counter'] == preferredCounter:
                return index
        for (index, card) in enumerate(get_hand(player)):
            cardInfo = get_card_info(card)
            if cardInfo['counter'] > 0:
                return index
    return 'e'

def ai_counter_late_characters(player, attackerPower, targetPower, target):
    counterNeeded = attackerPower - targetPower + 1000
    if counterNeeded <= 0:
        return 'e'
    maxCounter = 0
    for card in get_hand(player):
        cardInfo = get_card_info(card)
        if cardInfo['type'] == 'character' and cardInfo['counter'] > 0:
            maxCounter += cardInfo['counter']

    if maxCounter < counterNeeded:
        return 'e'

    if counterNeeded == 1000:
        preferredCounter = 1000
    else:
        preferredCounter = 2000

    if target['type'] == 'leader':
        if get_life_count(player) > 3 and counterNeeded > 1000:
            return 'e'
    if target['type'] == 'character':
        if get_life_count(player) > 3 and counterNeeded > 2000:
            return 'e'

    for (index, card) in enumerate(get_hand(player)):
        cardInfo = get_card_info(card)
        if cardInfo['counter'] == preferredCounter:
            return index
    for (index, card) in enumerate(get_hand(player)):
        cardInfo = get_card_info(card)
        if cardInfo['counter'] > 0:
            return index
    return 'e'

def ai_counter_early_characters(player, attackerPower, targetPower, target):
    # If life is less than 3, counter with all there is.
    counterNeeded = attackerPower - targetPower + 1000
    if counterNeeded <= 0:
        return 'e'
    maxCounter = 0
    for card in get_hand(player):
        cardInfo = get_card_info(card)
        if cardInfo['type'] == 'character' and cardInfo['counter'] > 0:
            maxCounter += cardInfo['counter']

    if maxCounter < counterNeeded:
        return 'e'

    if counterNeeded == 1000:
        preferredCounter = 1000
    else:
        preferredCounter = 2000

    if target['type'] == 'leader' and get_life_count(player) > 5:
        return 'e'
    if target['type'] == 'character':
        if get_life_count(player) > 3 and counterNeeded > 2000:
            return 'e'

    for (index, card) in enumerate(get_hand(player)):
        cardInfo = get_card_info(card)
        if cardInfo['counter'] == preferredCounter:
            return index
    for (index, card) in enumerate(get_hand(player)):
        cardInfo = get_card_info(card)
        if cardInfo['counter'] > 0:
            return index
    return 'e'

def getLowestCost(player):
    lowestCostIndex = getLowestCostCharacterIndex(player)
    if lowestCostIndex is None:
        return None
    lowestCostCharacter = get_character(player, lowestCostIndex)
    lowestCost = get_card_info(lowestCostCharacter['code'])['cost']
    return lowestCost

def checkPermanentCharacterPowerEffects(player, character):
    characterInfo = get_card_info(character['code'])
    power = checkPermanentPowerEffectsLeader(player, character)
    turnPlayer = get_turn_player()
    opponent = getOpponent(player)

    for character in get_characterList(opponent):
        info = get_card_info(character['code'])
        effect = info.get('effect', None)
        if effect == None:
            continue
        if effect['type'] != 'powerManipulation':
            continue
        if effect.get('turn') == 'yourTurn' and player != turnPlayer:
            continue
        target = effect['target']
        if target == 'yourCharacters':
            continue
        if target == 'opponentCharacters' and characterInfo['type'] != 'character':
            continue
        donCost = effect.get('donCost', 0)
        attachedDon = getAttachedDon(character)
        if attachedDon < donCost:
            continue
        power += effect['power']
    return power

def checkPermanentPowerEffectsLeader(player, character):
    characterInfo = get_card_info(character['code'])
    power = 0
    turnPlayer = get_turn_player()
    turnLeader = get_leader(turnPlayer)
    info = get_card_info(turnLeader['code'])
    effect = info.get('effect', None)
    if effect == None:
        return power
    if effect['type'] != 'powerManipulation':
        return power
    if effect['turn'] == 'yourTurn' and player != turnPlayer:
        return power
    target = effect['target']
    if target == 'yourCharacters' and characterInfo['type'] != 'character':
        return power
    donCost = effect.get('donCost', 0)
    attachedDon = getAttachedDon(turnLeader)
    if attachedDon < donCost:
        return power
    power += effect['power']
    return power

def resolveEffect(player, character):
    info = get_card_info(character['code'])
    effect = info.get('effect')
    if effect is None:
        return
    type = effect['type']
    if type == 'search':
        quantity = effect['quantity']
        archeTypes = effect['searchType']
        cards = revealCards(player, quantity)
        addedCard = None
        for card in cards:
            cardInfo = get_card_info(card)
            cardArcheTypes = cardInfo['archetype']
            intersection = list(set(archeTypes) & set(cardArcheTypes))
            if len(intersection) > 0:
                addedCard = card
                addCardToHand(player, card)
                break
        if addedCard is not None:
            cards.remove(card)
        if len(cards) > 0:
            bottomDeck(player, cards)
    elif type == 'ignoreBlocker':
        duration = effect['duration']
        if duration == 'battle':
            opponent = getOpponent(player)
            game[opponent]['battleEffects'].append(effect)
        # todo implement turn duration

def resolveWhenAttackingEffect(player, character):
    info = get_card_info(character['code'])
    effect = info.get('effect')
    if effect is None:
        return
    if effect.get('trigger') != 'whenAttacking':
        return
    donCost = effect.get('donCost', 0)
    if donCost > 0:
        attachedDon = getAttachedDon(character)
        if attachedDon < donCost:
            return
    resolveEffect(player, character)

def getLeaderMove(player):
    leader = get_leader(player)
    code = leader['code']
    if code == 'OP01-001':
        return getRedZoroMove(player)
    elif code == 'ST11-001':
        return getGreenUtaMove(player)
    return None

def getRedZoroMove(player):
    if not player_is_allowed_to_attack():
        return None
    leader = get_leader(player)
    attachedDon = getAttachedDon(leader)
    if attachedDon > 0:
        return None
    availableDon = getAvailableDon(player)
    if availableDon < 1:
        return None
    highestCost = getHighestPlayableCostInHand(player)
    if availableDon == highestCost:
        return None
    leftDon = availableDon - 1
    numberOfCharactersAbleToAttack = getNumberOfCharactersAbleToAttack(player)
    for (index, card) in enumerate(get_hand(player)):
        info = get_card_info(card)
        if hasRush(card) and info['cost'] <= leftDon:
            numberOfCharactersAbleToAttack += 1
    if numberOfCharactersAbleToAttack == 0:
        return None
    return 'g:l:1'

def getGreenUtaMove(player):
    if not player_is_allowed_to_attack():
        return None
    leader = get_leader(player)
    attachedDon = getAttachedDon(leader)
    if attachedDon > 0:
        return None
    if not can_attack_with_leader(player):
        return None
    availableDon = getAvailableDon(player)
    if availableDon == 0:
        return None
    highestCost = getHighestPlayableCostInHand(player)
    if availableDon == highestCost:
        return None
    return 'g:l:1'

def canGoForLethal(player):
    # @todo take opponent counter into account
    playerTurn = get_turn_player()
    opponent = getOpponent(player)
    opponentLeaderPower = getLeaderPower(opponent)
    opponentLife = get_life_count(opponent)
    requiredHits = opponentLife + 1
    availableDon = getAvailableDon(player)
    if playerTurn != player:
        availableDon += 2
        if availableDon > 10:
            availableDon = 10
   
    leaderAttack = 1 if playerTurn != player or can_attack_with_leader(player) else 0
    numberOfPossibleHits = leaderAttack
    characterList = get_characterList(player)
    sortedCharacters = characterList.copy()
    sortedCharacters.sort(key=sortCharactersByPower, reverse=True)
    leftDon = availableDon
    if playerTurn == player:
        for card in get_hand(player):
            info = get_card_info(card)
            if hasRush(card) and leftDon >= info['cost'] and info['power'] >= opponentLeaderPower:
                numberOfPossibleHits += 1
                leftDon -= info['cost']

    for character in sortedCharacters:
        index = characterList.index(character)
        if playerTurn == player and not can_attack_with_character(player, index):
            continue
        power = getCharacterPower(player, character)
        if power < opponentLeaderPower:
            diff = opponentLeaderPower - power
            quantity = int(diff / 1000)
            if quantity > leftDon:
                break
            leftDon -= quantity
        numberOfPossibleHits += 1
    if numberOfPossibleHits < requiredHits:
        return False
    return True

def goForLethal(player):
    opponent = getOpponent(player)
    opponentLeaderPower = getLeaderPower(opponent)
    availableDon = getAvailableDon(player)

    # Play rush characters
    if getNumberOfPlayerCharacters(player) < 5:
        for (index, card) in enumerate(get_hand(player)):
            info = get_card_info(card)
            if hasRush(card) and can_play_card(player, index) and info['power'] >= opponentLeaderPower:
                return 'c:' + str(index)

    characterList = get_characterList(player)
    sortedCharacters = characterList.copy()
    # First distribute DON!! to most powerful to least powerful characters
    # so that they reach at least the same power as the opponent leader.
    sortedCharacters.sort(key=sortCharactersByPower, reverse=True)
    for (index, character) in enumerate(sortedCharacters):
        indexCharacter = characterList.index(character)
        characterPower = getCharacterPower(player, character)
        if characterPower < opponentLeaderPower:
            diff = opponentLeaderPower - characterPower
            quantity = int(diff / 1000)
            if quantity > availableDon:
                break
            return 'g:' + str(indexCharacter) + ':' + str(quantity)
    # If there is still DON!! left, then distribute it evenly under the leader and characters with at least the opponent leader power.
    if availableDon > 0:
        indexLowestAttacker = 'l'
        lastLowestPower = getLeaderPower(player)
        for (index, character) in enumerate(characterList):
            characterPower = getCharacterPower(player, character)
            if characterPower >= opponentLeaderPower and (lastLowestPower is None or (characterPower < lastLowestPower)):
                indexLowestAttacker = index
                lastLowestPower = characterPower
        if indexLowestAttacker is not None:
            return 'g:' + str(indexLowestAttacker) + ':1'
    # Attack leader with leader
    if can_attack_with_leader(player):
        return 'b:l:l'
    # Attack with lowest to strongest character
    sortedCharactersAscending = characterList.copy()
    sortedCharactersAscending.sort(key=sortCharactersByPower)
    for character in sortedCharactersAscending:
        index = characterList.index(character)
        characterPower = getCharacterPower(player, character)
        if can_attack_with_character(player, index) and characterPower >= opponentLeaderPower:
            return 'b:' + str(index) + ':l'
    return 'e'

def sortCharactersByPower(character):
    info = get_card_info(character['code'])
    return info['power']

def getHighestPlayableCostInHand(player, reservedDon = 0):
    highestCost = 0
    highestCostIndex = getHighestPlayableCostCharacterIndexInHand(player, reservedDon)
    if highestCostIndex is not None:
        highestCostCard = get_card(player, highestCostIndex)
        highestCost = get_card_info(highestCostCard)['cost']
    return highestCost

def getHighestPlayableBlockerCostInHand(player):
    highestCost = 0
    highestCostIndex = getHighestPlayableCostBlockerCharacterIndexInHand(player)
    if highestCostIndex is not None:
        highestCostCard = get_card(player, highestCostIndex)
        highestCost = get_card_info(highestCostCard)['cost']
    return highestCost

def getHighestPlayableCostCharacterIndexInHand(player, reservedDon = 0):
    hand = get_hand(player)
    if len(hand) == 0:
        return None
    currentIndex = None
    currentWeight = None
    for index, card in enumerate(get_hand(player)):
        info = get_card_info(card)
        if info['type'] != 'character':
            continue
        weight = info['cost'] * int((2000 - info['counter']) / 1000)
        if can_play_card(player, index, reservedDon) and (currentIndex is None or weight > currentWeight):
            currentIndex = index
            currentWeight = weight
    if currentWeight == 0:
        return None
    return currentIndex

def getHighestPlayableCostBlockerCharacterIndexInHand(player):
    hand = get_hand(player)
    if len(hand) == 0:
        return None
    currentIndex = None
    currentWeight = None
    for index, card in enumerate(get_hand(player)):
        info = get_card_info(card)
        if not hasBlocker(card):
            continue
        weight = info['cost'] * int((2000 - info['counter']) / 1000)
        if can_play_card(player, index) and (currentIndex is None or weight > currentWeight):
            currentIndex = index
            currentWeight = weight
    if currentWeight == 0:
        return None
    return currentIndex

def getLowestCostCharacterIndex(player):
    characters = get_characterList(player)
    if len(characters) == 0:
        return None
    lowestCost = None
    lowestCostIndex = None
    for (index, character) in enumerate(characters):
        info = get_card_info(character['code'])
        if lowestCost is None or info['cost'] < lowestCost:
            lowestCostIndex = index
            lowestCost = info['cost']
    return lowestCostIndex

def manual_counter(player, attackerPower, targetPower):
    while True:
        printHand(player)
        print('Attacker power: ' + str(attackerPower))
        print('Your power: ' + str(targetPower))
        print('Choose card to counter or exit (e)')
        counter = input()
        if counter == 'e':
            return 'e'
        try:
            counter = int(counter)
        except:
            continue
        counterIndex = counter - 1
        return counterIndex

def get_manual_move(player):
    while True:
        print_actions()
        action = input()
        if action == 'c':
            printAvailableDon(player)
            printHand(player)
            cardToPlay = input()
            try:
                cardToPlay = int(cardToPlay)
            except:
                continue
            handIndex = cardToPlay - 1
            if not hand_card_exists_at_index(player, handIndex):
                print('')
                print('Invalid input')
                continue
            if not can_play_card(player, handIndex):
                print('')
                print('Not enough DON!!')
                continue
            return 'c:' + str(handIndex)
        elif action == 'b':
            if not player_is_allowed_to_attack():
                print('')
                print('You can\'t attack on your first turn')
                continue
            printBoard(player)
            print('')
            print('Choose character or leader (l) to attack with')
            characterToAttackWith = input()
            if characterToAttackWith == 'l':
                if not can_attack_with_leader(player):
                    print('')
                    print('You can\'t attack with your leader')
                    continue
                characterToAttackWithIndex = 'l'
            else:
                try:
                    characterToAttackWith = int(characterToAttackWith)
                except:
                    continue
                characterToAttackWithIndex = characterToAttackWith - 1
                if not character_exists_at_index(player, characterToAttackWithIndex):
                    print('')
                    print('Invalid input')
                    continue
                if not can_attack_with_character(player, characterToAttackWithIndex):
                    print('')
                    print('You can\'t attack with this character')
                    continue
            printBoard(player)
            print('Choose target character or leader (l) to attack')
            attackTarget = input()
            if attackTarget == 'l':
                attackTargetIndex = 'l'
            else:
                try:
                    attackTarget = int(attackTarget)
                except:
                    continue
                attackTargetIndex = attackTarget - 1
                if not character_exists_at_index(getOpponent(player), attackTargetIndex):
                    print('')
                    print('Invalid input')
                    continue
                if not can_attack_character(player, attackTargetIndex):
                    print('')
                    print('You can\'t attack this character')
                    continue
            return 'b:' + str(characterToAttackWithIndex) + ':' + str(attackTargetIndex)
        elif action == 'g':
            printPlayerBoard(player)
            print('')
            print('Choose character or leader (l) to attach DON!! to')
            characterToattach_donTo = input()
            if characterToattach_donTo == 'l':
                characterToattach_donToIndex = 'l'
            else:
                try:
                    characterToattach_donTo = int(characterToattach_donTo)
                except:
                    continue
                characterToattach_donToIndex = characterToattach_donTo - 1
                if not character_exists_at_index(player, characterToattach_donToIndex):
                    print('')
                    print('Invalid input')
                    continue
            print('')
            print('How many DON!!?')
            try:
                numberOfDonToAttachTo = int(input())
            except:
                print('Invalid input')
                continue    
            return 'g:' + str(characterToattach_donToIndex) + ':' + str(numberOfDonToAttachTo)
        elif action == 'e':
            return 'e'

deck1 = deck.create('decks/ST01 - Strawhat.deck')
deck2 = deck.create('decks/ST04 - Animal Kingdom.deck')

game = {
    'turn': 0,
    'playerTurn': None,
    PLAYER1: {
        'deck': deck1['deck'],
        'leader': deck1['leader'],
        'field': {
            'leader': {
                'code': deck1['leader'],
                'status': 'active',
                'powerIncreaseBattle': 0,
                'attachedDon': 0,
            },
            'stage': {},
            'characters': [],
            'don': {'active': 0, 'rested': 0}
        },
        'hand': [],
        'trash': [],
        'life': [],
        'don_deck': 10,
        'battleEffects': []
    },
    PLAYER2: {
        'deck': deck2['deck'],
        'leader': deck2['leader'],
        'field': {
            'leader': {
                'code': deck2['leader'],
                'status': 'active',
                'powerIncreaseBattle': 0,
                'attachedDon': 0,
            },
            'stage': {},
            'characters': [],
            'don': {'active': 0, 'rested': 0}
        },
        'hand': [],
        'trash': [],
        'life': [],
        'don_deck': 10,
        'battleEffects': []
    },
}

def ai_move1(player):
    move = ai_move_aggro(player)
    return move

def ai_move2(player):
    #return get_manual_move(player)
    move = ai_move_control(player)
    return move

def ai_counter1(player, attackerPower, targetPower, target):
    move = ai_counter_early_characters(player, attackerPower, targetPower, target)
    return move

def ai_counter2(player, attackerPower, targetPower, target):
    #return manual_counter(player, attackerPower, targetPower)
    move = ai_counter_early_characters(player, attackerPower, targetPower, target)
    return move

shuffle_deck(PLAYER1)
shuffle_deck(PLAYER2)
draw_cards(PLAYER1, 5)
draw_cards(PLAYER2, 5)
init_life(PLAYER1)
init_life(PLAYER2)
while True:
    next_turn()
    player_action()
    printBoard(PLAYER1)
