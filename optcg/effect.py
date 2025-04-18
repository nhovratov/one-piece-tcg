import optcg.info as info
import optcg.state as state
import optcg.util as util
from optcg.state import game
import optcg.action as action

def checkPermanentCharacterPowerEffects(player, character):
    characterInfo = info.get_card_info(character['code'])
    power = checkPermanentPowerEffectsLeader(player, character)
    turnPlayer = state.get_turn_player()
    opponent = util.getOpponent(player)

    for character in state.get_characters(opponent):
        card_info = info.get_card_info(character['code'])
        effect = card_info.get('effect', None)
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
        attachedDon = state.get_attached_don(character)
        if attachedDon < donCost:
            continue
        power += effect['power']
    return power

def checkPermanentPowerEffectsLeader(player, character):
    character_info = info.get_card_info(character['code'])
    power = 0
    turnPlayer = state.get_turn_player()
    turnLeader = state.get_leader(turnPlayer)
    card_info_leader = info.get_card_info(turnLeader['code'])
    effect = card_info_leader.get('effect', None)
    if effect == None:
        return power
    if effect['type'] != 'powerManipulation':
        return power
    if effect['turn'] == 'yourTurn' and player != turnPlayer:
        return power
    target = effect['target']
    if target == 'yourCharacters' and character_info['type'] != 'character':
        return power
    donCost = effect.get('donCost', 0)
    attachedDon = state.get_attached_don(turnLeader)
    if attachedDon < donCost:
        return power
    power += effect['power']
    return power

def resolve_effect(player, character, arguments = []):
    card_info = info.get_card_info(character['code'])
    effect = card_info.get('effect')
    if effect is None:
        return
    restriction = effect.get('restriction')
    if restriction is not None:
        if restriction == 'oncePerTurn':
            effect_used_this_turn = character.get('effect_used_this_turn')
            if effect_used_this_turn:
                return
    type = effect['type']
    if type == 'search':
        quantity = effect['quantity']
        archeTypes = effect['searchType']
        cards = action.revealCards(player, quantity)
        addedCard = None
        for card in cards:
            card_info = info.get_card_info(card)
            cardArcheTypes = card_info['archetype']
            intersection = list(set(archeTypes) & set(cardArcheTypes))
            if len(intersection) > 0:
                addedCard = card
                action.addCardToHand(player, card)
                break
        if addedCard is not None:
            cards.remove(card)
        if len(cards) > 0:
            action.bottom_deck(player, cards)
    elif type == 'ignoreBlocker':
        duration = effect['duration']
        if duration == 'battle':
            opponent = util.getOpponent(player)
            game[opponent]['battleEffects'].append(effect)
    elif type == 'giveRestedDon':
        if arguments == []:
            print('Choose target')
            target = input()
        else:
            target = arguments[0]
        if target != 'l':
            target = int(target)
        # todo: Allow to specify quantity as well.
        quantity = int(effect['quantity'])
        action.attach_rested_don(player, target, quantity)
    if restriction == 'oncePerTurn':
        character['effect_used_this_turn'] = True
        # todo implement turn duration

def resolveWhenAttackingEffect(player, character):
    card_info = info.get_card_info(character['code'])
    effect = card_info.get('effect')
    if effect is None:
        return
    if effect.get('trigger') != 'whenAttacking':
        return
    donCost = effect.get('donCost', 0)
    if donCost > 0:
        attached_don = state.get_attached_don(character)
        if attached_don < donCost:
            return
    resolve_effect(player, character)

def can_be_activated(player, character):
    card_info = info.get_card_info(character['code'])
    effect = card_info.get('effect')
    if effect is None:
        return False
    if effect.get('trigger') != 'activateMain':
        return False
    restriction = effect.get('restriction')
    if restriction is not None:
        if restriction == 'oncePerTurn':
            effect_used_this_turn = character.get('effect_used_this_turn')
            if effect_used_this_turn:
                return False
    return True