import optcg.state as state
import optcg.effect as effect

def get_character_power(player, character):
    power = state.get_character_power(player, character)
    power += effect.checkPermanentCharacterPowerEffects(player, character)
    return power

def get_leader_power(player):
    leader = state.get_leader(player)
    power = state.get_leader_power(player)
    power += effect.checkPermanentCharacterPowerEffects(player, leader)
    return power