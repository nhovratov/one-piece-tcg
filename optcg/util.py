import optcg.state as state
import optcg.info as info
import optcg.rule as rule

def getOpponent(player):
    return 'player2' if player == 'player1' else 'player1'

def getHighestPlayableCostInHand(player, reservedDon = 0):
    highestCost = 0
    highestCostIndex = getHighestPlayableCostCharacterIndexInHand(player, reservedDon)
    if highestCostIndex is not None:
        highestCostCard = state.get_card(player, highestCostIndex)
        highestCost = info.get_card_info(highestCostCard)['cost']
    return highestCost

def getHighestPlayableBlockerCostInHand(player):
    highestCost = 0
    highestCostIndex = getHighestPlayableCostBlockerCharacterIndexInHand(player)
    if highestCostIndex is not None:
        highestCostCard = state.get_card(player, highestCostIndex)
        highestCost = info.get_card_info(highestCostCard)['cost']
    return highestCost

def getHighestPlayableCostCharacterIndexInHand(player, reservedDon = 0):
    hand = state.get_hand(player)
    if len(hand) == 0:
        return None
    currentIndex = None
    currentWeight = None
    for index, card in enumerate(hand):
        card_info = info.get_card_info(card)
        if card_info['type'] != 'character':
            continue
        weight = card_info['cost'] * int((2000 - card_info['counter']) / 1000)
        if rule.can_play_card(player, index, reservedDon) and (currentIndex is None or weight > currentWeight):
            currentIndex = index
            currentWeight = weight
    if currentWeight == 0:
        return None
    return currentIndex

def getHighestPlayableCostBlockerCharacterIndexInHand(player):
    hand = state.get_hand(player)
    if len(hand) == 0:
        return None
    currentIndex = None
    currentWeight = None
    for index, card in enumerate(hand):
        card_info = info.get_card_info(card)
        if not info.hasBlocker(card):
            continue
        weight = card_info['cost'] * int((2000 - card_info['counter']) / 1000)
        if rule.can_play_card(player, index) and (currentIndex is None or weight > currentWeight):
            currentIndex = index
            currentWeight = weight
    if currentWeight == 0:
        return None
    return currentIndex

def getLowestCostCharacterIndex(player):
    characters = state.get_characterList(player)
    if len(characters) == 0:
        return None
    lowestCost = None
    lowestCostIndex = None
    for (index, character) in enumerate(characters):
        card_info = info.get_card_info(character['code'])
        if lowestCost is None or card_info['cost'] < lowestCost:
            lowestCostIndex = index
            lowestCost = card_info['cost']
    return lowestCostIndex

def getLowestCost(player):
    lowestCostIndex = getLowestCostCharacterIndex(player)
    if lowestCostIndex is None:
        return None
    lowestCostCharacter = state.get_character(player, lowestCostIndex)
    lowestCost = info.get_card_info(lowestCostCharacter['code'])['cost']
    return lowestCost

def getNumberOfCharactersAbleToAttack(player):
    activeCharacters = []
    for (index, character) in enumerate(state.get_characterList(player)):
        if rule.can_attack_with_character(player, index):
            activeCharacters.append(character)
    return len(activeCharacters)