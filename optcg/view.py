from tabulate import tabulate
import optcg.info as info
from optcg.log import log
import optcg.state as state
import optcg.util as util
import optcg.calc as calc

def printAvailableDon(player):
    log('DON!!: ' + str(state.get_available_don(player)))

def printNumberOfCardsInHand(player):
    log('Number of cards in hand: ' + str(len(state.get_hand(player))))

def printStatus(player):
    log('')
    table = [[state.get_life_count(player), state.get_available_don(player), state.get_number_of_cards_in_hand(player)]]
    headers = ['Life', 'DON!!', 'Hand size']
    log(tabulate(table, headers=headers, tablefmt="grid", disable_numparse=True))

def printHand(player):
    log('')
    counter = 1
    table = []
    for card in state.get_hand(player):
        card_info = info.get_card_info(card)
        parts = [
            str(counter) + ':',
            '[' + card + ']',
            card_info['name'],
            '(' + str(card_info['cost']) + ')',
            card_info['power'],
            card_info['counter']
        ]
        table.append(parts)
        counter += 1
    log(tabulate(table, headers=['', 'Code', 'Name', 'Cost', 'Power', 'Counter'], disable_numparse=True))

def printLeader(player):
    log('')
    leader = state.get_leader(player)
    card_info = info.get_card_info(leader['code'])
    parts = [
        '[' + card_info['code'] + ']',
        card_info['name'],
        calc.get_character_power(player, leader),
        '↑ (active)' if leader['status'] == 'active' else '→ (rested)',
    ]
    log(tabulate([parts], headers=['Leader', 'Name', 'Power', 'Status'], tablefmt="grid", disable_numparse=True))

def printCharacters(player):
    log('')
    counter = 1
    table = []
    for character in state.get_characterList(player):
        card = character['code']
        cardInfo = info.get_card_info(character['code'])
        parts = [
            str(counter) + ':',
            '[' + card + ']',
            cardInfo['name'],
            '(' + str(cardInfo['cost']) + ')',
            calc.get_character_power(player, character),
            '↑ (active)' if character['status'] == 'active' else '→ (rested)',
            'Yes' if character['isExhausted'] else '',
        ]
        table.append(parts)
        counter += 1
    log(tabulate(table, headers=['', 'Code', 'Name', 'Cost', 'Power', 'Status', 'Exhausted'], tablefmt="grid", disable_numparse=True))

def printBoard(player):
    opponent = util.getOpponent(player)
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