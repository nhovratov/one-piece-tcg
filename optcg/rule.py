import optcg.state as state
import optcg.util as util
import optcg.info as info
import optcg.calc as calc
from optcg.state import game

def player_is_allowed_to_attack():
    turn = state.get_game_turn()
    return turn > 2

def can_attack_with_character(player, index):
    character = state.get_character(player, index)
    if character['status'] == 'rested' or character['isExhausted']:
        return False
    return True

def can_attack_with_leader(player):
    leader = state.get_leader(player)
    if leader['status'] == 'rested':
        return False
    return True

def can_attack_character(player, index):
    opponent = util.getOpponent(player)
    character = state.get_character(opponent, index)
    if character['status'] == 'active':
        return False
    return True

def can_counter(player):
    hand = state.get_hand(player)
    for card in hand:
        cardInfo = info.get_card_info(card)
        if cardInfo['type'] == 'character' and cardInfo['counter'] > 0:
            return True
    return False

def can_play_card(player, index, reservedDon = 0):
    card = state.get_hand(player)[index]
    cardInfo = info.get_card_info(card)
    availableDon = state.get_available_don(player)
    availableDon -= reservedDon
    return cardInfo['cost'] <= availableDon

def canBlock(player):
    ignoreBlockerEffect = None
    for effect in game[player]['battleEffects']:
        if effect['type'] == 'ignoreBlocker':
            ignoreBlockerEffect = effect
            break
    characterList = state.get_characterList(player)
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
            return True
    return False