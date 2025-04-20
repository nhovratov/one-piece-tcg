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

    for field_character in state.get_characters(player):
        card_info = info.get_card_info(field_character['code'])
        effects = card_info.get('effect', None)
        if effects == None:
            continue
        for effect in effects:
            if effect['type'] != 'powerManipulation':
                continue
            if effect.get('trigger') is not None:
                continue
            if effect.get('turn') == 'yourTurn' and player != turnPlayer:
                continue
            target = effect['target']
            if target == 'opponentCharacters':
                continue
            if target == 'yourCharacters' and characterInfo['type'] != 'character':
                continue
            if target == 'self' and character is not field_character:
                continue
            needed_attached_don = effect.get('attachedDon')
            if needed_attached_don is not None:
                attached_don = state.get_attached_don(field_character)
                if attached_don < needed_attached_don:
                    continue
            power += effect['power']

    for field_character in state.get_characters(opponent):
        card_info = info.get_card_info(field_character['code'])
        effects = card_info.get('effect', None)
        if effects == None:
            continue
        for effect in effects:
            if effect['type'] != 'powerManipulation':
                continue
            if effect.get('trigger') is not None:
                continue
            if effect.get('turn') == 'yourTurn' and player != turnPlayer:
                continue
            target = effect['target']
            if target == 'yourCharacters':
                continue
            if target == 'self':
                continue
            if target == 'opponentCharacters' and characterInfo['type'] != 'character':
                continue
            needed_attached_don = effect.get('attachedDon')
            if needed_attached_don is not None:
                attached_don = state.get_attached_don(field_character)
                if needed_attached_don < attached_don:
                    continue
            power += effect['power']

    return power

def checkPermanentPowerEffectsLeader(player, character):
    character_info = info.get_card_info(character['code'])
    power = 0
    turnPlayer = state.get_turn_player()
    turnLeader = state.get_leader(turnPlayer)
    card_info_leader = info.get_card_info(turnLeader['code'])
    effects = card_info_leader.get('effect')
    if effects == None:
        return power
    for effect in effects:
        if effect['type'] != 'powerManipulation':
            return power
        if effect['turn'] == 'yourTurn' and player != turnPlayer:
            return power
        target = effect['target']
        if target == 'yourCharacters' and character_info['type'] != 'character':
            return power
        needed_attached_don = effect.get('attachedDon')
        if needed_attached_don is not None:
            attached_don = state.get_attached_don(turnLeader)
            if attached_don < needed_attached_don:
                return power
        power += effect['power']
    return power

def resolve_trigger_effect(player, trigger_card, arguments = []):
    card_info = info.get_card_info(trigger_card)
    effect = card_info.get('triggerEffect')
    if effect is None:
        return
    resolve_effect(player, {}, effect, arguments)

def resolve_card_effect(player, effect_card, effect_index, arguments = []):
    card_info = info.get_card_info(effect_card['code'])
    effects = card_info.get('effect')
    if effects is None:
        return
    if len(effects) <= effect_index:
        return
    effect = effects[effect_index]
    resolve_effect(player, effect_card, effect, arguments)

def resolve_effect(player, effect_card, effect, arguments = []):
    restriction = effect.get('restriction')
    if restriction is not None:
        if restriction == 'oncePerTurn':
            effect_used_this_turn = effect_card.get('effect_used_this_turn')
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
    elif type == 'gainRush' and state.is_exhausted(effect_card):
        action.rush_character(effect_card)
    elif type == 'powerManipulation':
        power = effect['power']
        # todo: Check valid target
        viable_target = effect['target']
        # No target selected
        if arguments == []:
            return
        chosen_target = arguments[0]
        action.manipulate_turn_power_of_leader_or_character(player, chosen_target, power)
    if restriction == 'oncePerTurn':
        effect_card['effect_used_this_turn'] = True
        # todo implement turn duration

def resolve_when_attaching_don(player, character):
    card_info = info.get_card_info(character['code'])
    effects = card_info.get('effect')
    if effects is None:
        return
    for effect in effects:
        # The effect is activated as soon as enough DON is attached.
        if not 'attachedDon' in effect:
            return
        if 'trigger' in effect:
            return
        if state.get_attached_don(character) < effect['attachedDon']:
            return
        resolve_card_effect(player, character, 0)

def resolveWhenAttackingEffect(player, character, arguments = []):
    card_info = info.get_card_info(character['code'])
    effects = card_info.get('effect')
    if effects is None:
        return
    if len(effects) == 0:
        return
    for (index, effect) in enumerate(effects):
        if effect.get('trigger') != 'whenAttacking':
            return
        needed_attached_don = effect.get('attachedDon', 0)
        if needed_attached_don > 0:
            attached_don = state.get_attached_don(character)
            if attached_don < needed_attached_don:
                return
        resolve_card_effect(player, character, index, arguments)

def can_be_activated(player, character):
    effect_index = 0
    card_info = info.get_card_info(character['code'])
    effects = card_info.get('effect')
    if effects is None:
        return False
    if len(effects) <= effect_index:
        return False
    effect = effects[effect_index]
    if effect.get('trigger') != 'activateMain':
        return False
    restriction = effect.get('restriction')
    if restriction is not None:
        if restriction == 'oncePerTurn':
            effect_used_this_turn = character.get('effect_used_this_turn')
            if effect_used_this_turn:
                return False
    return True