import optcg.view as view
import optcg.rule as rule
import optcg.state as state
import optcg.util as util

def manual_counter(player, attackerPower, targetPower):
    while True:
        view.printHand(player)
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
        view.print_actions()
        action = input()
        if action == 'c':
            view.printAvailableDon(player)
            view.printHand(player)
            cardToPlay = input()
            try:
                cardToPlay = int(cardToPlay)
            except:
                continue
            handIndex = cardToPlay - 1
            if not state.hand_card_exists_at_index(player, handIndex):
                print('')
                print('Invalid input')
                continue
            if not rule.can_play_card(player, handIndex):
                print('')
                print('Not enough DON!!')
                continue
            return 'c:' + str(handIndex)
        elif action == 'b':
            if not rule.player_is_allowed_to_attack():
                print('')
                print('You can\'t attack on your first turn')
                continue
            view.printBoard(player)
            print('')
            print('Choose character or leader (l) to attack with')
            characterToAttackWith = input()
            if characterToAttackWith == 'l':
                if not rule.can_attack_with_leader(player):
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
                if not state.character_exists_at_index(player, characterToAttackWithIndex):
                    print('')
                    print('Invalid input')
                    continue
                if not rule.can_attack_with_character(player, characterToAttackWithIndex):
                    print('')
                    print('You can\'t attack with this character')
                    continue
            view.printBoard(player)
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
                opponent = util.getOpponent(player)
                if not state.character_exists_at_index(opponent, attackTargetIndex):
                    print('')
                    print('Invalid input')
                    continue
                if not rule.can_attack_character(player, attackTargetIndex):
                    print('')
                    print('You can\'t attack this character')
                    continue
            return 'b:' + str(characterToAttackWithIndex) + ':' + str(attackTargetIndex)
        elif action == 'g':
            view.printPlayerBoard(player)
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
                if not state.character_exists_at_index(player, characterToattach_donToIndex):
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

