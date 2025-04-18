import optcg.state as state
import optcg.util as util
import optcg.info as info
import optcg.rule as rule
import optcg.calc as calc
import optcg.effect as effect

ai_move1_method = None
ai_move2_method = None
ai_counter1_method = None
ai_counter2_method = None

def set_ai_move1(move):
    global ai_move1_method
    ai_move1_method = move

def set_ai_move2(move):
    global ai_move2_method
    ai_move2_method = move

def set_ai_counter_move1(move):
    global ai_counter1_method
    ai_counter1_method = move

def set_ai_counter_move2(move):
    global ai_counter2_method
    ai_counter2_method = move

def ai_move1(player):
    move = ai_move1_method(player)
    return move

def ai_move2(player):
    move = ai_move2_method(player)
    return move

def ai_counter1(player, attackerPower, targetPower, target):
    move = ai_counter1_method(player, attackerPower, targetPower, target)
    return move

def ai_counter2(player, attackerPower, targetPower, target):
    move = ai_counter2_method(player, attackerPower, targetPower, target)
    return move

def ai_counter_early_characters(player, attackerPower, targetPower, target):
    # If life is less than 3, counter with all there is.
    counterNeeded = attackerPower - targetPower + 1000
    if counterNeeded <= 0:
        return 'e'
    maxCounter = 0
    for card in state.get_hand(player):
        cardInfo = info.get_card_info(card)
        if cardInfo['type'] == 'character' and cardInfo['counter'] > 0:
            maxCounter += cardInfo['counter']

    if maxCounter < counterNeeded:
        return 'e'

    if counterNeeded == 1000:
        preferredCounter = 1000
    else:
        preferredCounter = 2000

    if target['type'] == 'leader' and state.get_life_count(player) > 5:
        return 'e'
    if target['type'] == 'character':
        if state.get_life_count(player) > 3 and counterNeeded > 2000:
            return 'e'

    for (index, card) in enumerate(state.get_hand(player)):
        cardInfo = info.get_card_info(card)
        if cardInfo['counter'] == preferredCounter:
            return index
    for (index, card) in enumerate(state.get_hand(player)):
        cardInfo = info.get_card_info(card)
        if cardInfo['counter'] > 0:
            return index
    return 'e'

def ai_move_aggro(player):
    leaderMove = getLeaderMove(player)
    if leaderMove is not None:
        return leaderMove
    opponent = util.getOpponent(player)
    if canGoForLethal(player) or canGoForLethal(opponent):
        return goForLethal(player)
    availableDon = state.get_available_don(player)
    powerOpponentLeader = calc.get_leader_power(opponent)
    highestCostIndex = util.get_highest_playable_cost_character_index_in_hand(player)
    highestCost = util.getHighestPlayableCostInHand(player)
    availableDonForBattle = availableDon - highestCost

    if not rule.player_is_allowed_to_attack():
        return 'e'
    # Attack with characters:
    characters = state.get_characters(player)
    sortedCharacters = characters.copy()
    sortedCharacters.sort(key=info.sortCharactersByPower)
    for character in sortedCharacters:
        index = characters.index(character)
        if not rule.can_attack_with_character(player, index):
            continue
        characterPower = calc.get_character_power(player, character)
        if characterPower >= powerOpponentLeader:
            return 'b:' + str(index) + ':l'
        elif characterPower + (availableDonForBattle * 1000) >= powerOpponentLeader:
            return 'g:' + str(index) + ':' + str(int((powerOpponentLeader - characterPower) / 1000))
    # Full aggro: give remaining DON to leader
    if availableDonForBattle > 0:
        return 'g:l:' + str(availableDonForBattle)
    # Attack leader with leader
    if rule.can_attack_with_leader(player):
        return 'b:l:l'
    # If there is enough DON to play a character, play that character.
    if highestCostIndex is not None:
        if state.get_number_of_player_characters(player) < 5:
            return 'c:' + str(highestCostIndex)
        # If board is full, check if there is something better to play.
        lowestCost = util.getLowestCost(player)
        lowestCostIndex = util.getLowestCostCharacterIndex(player)
        if highestCost > lowestCost:
            return 'c:' + str(highestCostIndex) + ':' + str(lowestCostIndex)
    return 'e'

def ai_move_control(player):
    leaderMove = getLeaderMove(player)
    if leaderMove is not None:
        return leaderMove
    opponent = util.getOpponent(player)
    if canGoForLethal(player) or canGoForLethal(opponent):
        return goForLethal(player)
    availableDon = state.get_available_don(player)
    powerLeader = calc.get_leader_power(player)
    powerOpponentLeader = calc.get_leader_power(opponent)
    # Prefer to play characters on curve
    highestBlockerCostIndex = None
    highestBlockerCost = 0
    highestCostIndex = util.get_highest_playable_cost_character_index_in_hand(player, highestBlockerCost)
    highestCost = util.getHighestPlayableCostInHand(player, highestBlockerCost)
    if highestCost != availableDon:
        highestBlockerCostIndex = util.getHighestPlayableCostBlockerCharacterIndexInHand(player)
        highestBlockerCost = util.getHighestPlayableBlockerCostInHand(player)
        highestCostIndex = util.get_highest_playable_cost_character_index_in_hand(player, highestBlockerCost)
        highestCost = util.getHighestPlayableCostInHand(player, highestBlockerCost)
    availableDonForBattle = availableDon - highestBlockerCost - highestCost

    if rule.player_is_allowed_to_attack():
        # Find rested characters
        characterToAttack = 'l'
        powerOpponentCharacter = calc.get_leader_power(opponent)
        for (index, character) in enumerate(state.get_characters(opponent)):
            if rule.can_attack_character(player, index):
                characterToAttack = index
                powerOpponentCharacter = calc.get_character_power(opponent, character)
                break
        # Attack with characters:
        for (index, character) in enumerate(state.get_characters(player)):
            if not rule.can_attack_with_character(player, index):
                continue
            if info.hasBlocker(character['code']):
                continue
            characterPower = calc.get_character_power(player, character)
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
        if rule.can_attack_with_leader(player):
            if powerOpponentCharacter > powerLeader:
                characterToAttack = 'l'
            return 'b:l:' + str(characterToAttack)

    # If there is enough DON to play a character, play that character.
    if highestBlockerCostIndex is not None:
        if state.get_number_of_player_characters(player) < 5:
            return 'c:' + str(highestBlockerCostIndex)
        # If board is full, check if there is something better to play.
        lowestCostIndex = util.getLowestCostCharacterIndex(player)
        return 'c:' + str(highestBlockerCostIndex) + ':' + str(lowestCostIndex)
    if highestCostIndex is not None:
        if state.get_number_of_player_characters(player) < 5:
            return 'c:' + str(highestCostIndex)
        # If board is full, check if there is something better to play.
        lowestCostIndex = util.getLowestCostCharacterIndex(player)
        lowestCost = util.getLowestCost(player)
        if highestCost > lowestCost:
            return 'c:' + str(highestCostIndex) + ':' + str(lowestCostIndex)

    return 'e'

def ai_counter_mid(player, attackerPower, targetPower, target):
    # If life is less than 3, counter with all there is.
    counterNeeded = attackerPower - targetPower + 1000
    if counterNeeded <= 0:
        return 'e'
    maxCounter = 0
    for card in state.get_hand(player):
        cardInfo = info.get_card_info(card)
        if cardInfo['type'] == 'character' and cardInfo['counter'] > 0:
            maxCounter += cardInfo['counter']

    if counterNeeded == 1000:
        preferredCounter = 1000
    else:
        preferredCounter = 2000

    if state.get_life_count(player) < 3 and maxCounter >= counterNeeded:
        for (index, card) in enumerate(state.get_hand(player)):
            cardInfo = info.get_card_info(card)
            if cardInfo['counter'] == preferredCounter:
                return index
        for (index, card) in enumerate(state.get_hand(player)):
            cardInfo = info.get_card_info(card)
            if cardInfo['counter'] > 0:
                return index
    return 'e'

def ai_counter_late_characters(player, attackerPower, targetPower, target):
    counterNeeded = attackerPower - targetPower + 1000
    if counterNeeded <= 0:
        return 'e'
    maxCounter = 0
    for card in state.get_hand(player):
        cardInfo = info.get_card_info(card)
        if cardInfo['type'] == 'character' and cardInfo['counter'] > 0:
            maxCounter += cardInfo['counter']

    if maxCounter < counterNeeded:
        return 'e'

    if counterNeeded == 1000:
        preferredCounter = 1000
    else:
        preferredCounter = 2000

    if target['type'] == 'leader':
        if state.get_life_count(player) > 3 and counterNeeded > 1000:
            return 'e'
    if target['type'] == 'character':
        if state.get_life_count(player) > 3 and counterNeeded > 2000:
            return 'e'

    for (index, card) in enumerate(state.get_hand(player)):
        cardInfo = info.get_card_info(card)
        if cardInfo['counter'] == preferredCounter:
            return index
    for (index, card) in enumerate(state.get_hand(player)):
        cardInfo = info.get_card_info(card)
        if cardInfo['counter'] > 0:
            return index
    return 'e'


def canGoForLethal(player):
    # @todo take opponent counter into account
    playerTurn = state.get_turn_player()
    opponent = util.getOpponent(player)
    opponentLeaderPower = calc.get_leader_power(opponent)
    opponentLife = state.get_life_count(opponent)
    requiredHits = opponentLife + 1
    availableDon = state.get_available_don(player)
    if playerTurn != player:
        availableDon += 2
        if availableDon > 10:
            availableDon = 10

    leaderAttack = 1 if playerTurn != player or rule.can_attack_with_leader(player) else 0
    numberOfPossibleHits = leaderAttack
    characterList = state.get_characters(player)
    sortedCharacters = characterList.copy()
    sortedCharacters.sort(key=info.sortCharactersByPower, reverse=True)
    leftDon = availableDon
    if playerTurn == player:
        for card in state.get_hand(player):
            card_info = info.get_card_info(card)
            if info.hasRush(card) and leftDon >= card_info['cost'] and card_info['power'] >= opponentLeaderPower:
                numberOfPossibleHits += 1
                leftDon -= card_info['cost']

    for character in sortedCharacters:
        index = characterList.index(character)
        if playerTurn == player and not rule.can_attack_with_character(player, index):
            continue
        power = calc.get_character_power(player, character)
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
    opponent = util.getOpponent(player)
    opponentLeaderPower = calc.get_leader_power(opponent)
    availableDon = state.get_available_don(player)

    # Play rush characters
    if state.get_number_of_player_characters(player) < 5:
        for (index, card) in enumerate(state.get_hand(player)):
            card_info = info.get_card_info(card)
            if info.hasRush(card) and rule.can_play_card(player, index) and card_info['power'] >= opponentLeaderPower:
                return 'c:' + str(index)

    characterList = state.get_characters(player)
    sortedCharacters = characterList.copy()
    # First distribute DON!! to most powerful to least powerful characters
    # so that they reach at least the same power as the opponent leader.
    sortedCharacters.sort(key=info.sortCharactersByPower, reverse=True)
    for (index, character) in enumerate(sortedCharacters):
        indexCharacter = characterList.index(character)
        characterPower = calc.get_character_power(player, character)
        if characterPower < opponentLeaderPower:
            diff = opponentLeaderPower - characterPower
            quantity = int(diff / 1000)
            if quantity > availableDon:
                break
            return 'g:' + str(indexCharacter) + ':' + str(quantity)
    # If there is still DON!! left, then distribute it evenly under the leader and characters with at least the opponent leader power.
    if availableDon > 0:
        indexLowestAttacker = 'l'
        lastLowestPower = calc.get_leader_power(player)
        for (index, character) in enumerate(characterList):
            characterPower = calc.get_character_power(player, character)
            if characterPower >= opponentLeaderPower and (
                    lastLowestPower is None or (characterPower < lastLowestPower)):
                indexLowestAttacker = index
                lastLowestPower = characterPower
        if indexLowestAttacker is not None:
            return 'g:' + str(indexLowestAttacker) + ':1'
    # Attack leader with leader
    if rule.can_attack_with_leader(player):
        return 'b:l:l'
    # Attack with lowest to strongest character
    sortedCharactersAscending = characterList.copy()
    sortedCharactersAscending.sort(key=info.sortCharactersByPower)
    for character in sortedCharactersAscending:
        index = characterList.index(character)
        characterPower = calc.get_character_power(player, character)
        if rule.can_attack_with_character(player, index) and characterPower >= opponentLeaderPower:
            return 'b:' + str(index) + ':l'
    return 'e'

def getLeaderMove(player):
    leader = state.get_leader(player)
    code = leader['code']
    if code == 'OP01-001':
        return getRedZoroMove(player)
    elif code == 'ST11-001':
        return getGreenUtaMove(player)
    elif code == 'ST01-001':
        return get_ST01_Luffy_move(player)
    return None

def get_ST01_Luffy_move(player):
    leader = state.get_leader(player)
    if not effect.can_be_activated(player, leader):
        return None
    # For now, just give leader the rested don.
    # Can be enhanced later to be able to attack with weaker characters.
    if state.get_rested_don(player) > 0:
        return 'a:l l'
    # If there is enough DON to play a character, play that character.
    highest_cost_index = util.get_highest_playable_cost_character_index_in_hand(player)
    if highest_cost_index is None:
        return None
    if state.get_number_of_player_characters(player) < 5:
        return 'c:' + str(highest_cost_index)
    return None

def getRedZoroMove(player):
    if not rule.player_is_allowed_to_attack():
        return None
    leader = state.get_leader(player)
    attachedDon = state.get_attached_don(leader)
    if attachedDon > 0:
        return None
    availableDon = state.get_available_don(player)
    if availableDon < 1:
        return None
    highestCost = util.getHighestPlayableCostInHand(player)
    if availableDon == highestCost:
        return None
    leftDon = availableDon - 1
    numberOfCharactersAbleToAttack = util.getNumberOfCharactersAbleToAttack(player)
    for (index, card) in enumerate(state.get_hand(player)):
        card_info = info.get_card_info(card)
        if info.hasRush(card) and card_info['cost'] <= leftDon:
            numberOfCharactersAbleToAttack += 1
    if numberOfCharactersAbleToAttack == 0:
        return None
    return 'g:l:1'

def getGreenUtaMove(player):
    if not rule.player_is_allowed_to_attack():
        return None
    leader = state.get_leader(player)
    attachedDon = state.get_attached_don(leader)
    if attachedDon > 0:
        return None
    if not rule.can_attack_with_leader(player):
        return None
    availableDon = state.get_available_don(player)
    if availableDon == 0:
        return None
    highestCost = util.getHighestPlayableCostInHand(player)
    if availableDon == highestCost:
        return None
    return 'g:l:1'