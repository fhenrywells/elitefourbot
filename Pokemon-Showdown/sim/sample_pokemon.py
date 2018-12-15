import pickle
from collections import defaultdict
from pprint import pprint

import pysim.pokemon_simple as sim
import pokemon_minimax

sample_pokemon = []


#pokemon1 = scyther, for stat boosts





#pokemon2 = vileplume, for status effects

#pokemon3 = machamp, supereffective moves

#baseline bot = snorlax


#run last part of pokemon_minimax.py to see what it would do

stat_multiplier = {"atk":1, "def": 1, "spa":1, "spd":1, "spe":1}

scyther = sim.Pokemon(
	123,
    110, #att 
    80, #def
    55, #sp att
    55, #sp def
    105, #speed
    70, #max hp
    74, #level
    1, #curr hp
    1, #generation
    ["slash", "swordsdance"],#, "agility", "hyperbeam"], #moves
    ["bug", "flying"], # types
    None, # status
    stat_multiplier # stat multiplier
   )

#		baseStats: {hp: 75, atk: 80, def: 85, spa: 100, spd: 100, spe: 50},

vileplume = sim.Pokemon(
	45,
	80,
	85,
	100,
	100,
	50,
	75,
	74,
	1,
	1,
	["sleeppowder", "bodyslam", "stunspore", "swordsdance"],
	["grass", "poison"],
	None, 
	stat_multiplier
	)

machamp = sim.Pokemon( # {hp: 90, atk: 130, def: 80, spa: 65, spd: 65, spe: 55},
	68,
	130,
	80,
	65,
	65,
	55,
	90,
	74,
	1,
	1,
	["hyperbeam", "earthquake", "submission", "rockslide"],
	["fighting"],
	None,
	stat_multiplier
	)

snorlax = sim.Pokemon( 
	143, #{hp: 160, atk: 110, def: 65, spa: 65, spd: 65, spe: 30},
	110,
	65,
	65,
	65,
	30,
	160,
	68,
	1,
	1,
	["bodyslam","rest"],# "thunderbolt", "blizzard"], #should replace rest with amnesia for vileplume games 
	["normal"],
	None,
	stat_multiplier
	)


#battle 1 scyther vs snorlax
agent = pokemon_minimax.MinimaxAgent() #can specify search depth here

#poke_id, attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types, status, stat_multipliers):
testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1.0, 1, ['hyperbeam', 'earthquake'], ['normal'], None, stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1.0, 1, ['tackle'], ['normal'], None, stat_multiplier)

action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print(testpoke1, testpoke2)
print("action is ", action) # should be earthquake at depth=2, hyperbeam at depth=1

#poke_id, attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types, status, stat_multipliers):
testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 90, 100, 90, 0.1, 1, ['quickattack', 'earthquake'], ['normal'], None, stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 0.1, 1, ['tackle'], ['normal'], None, stat_multiplier)

action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print(testpoke1, testpoke2)
print("action is ", action) # favor quickattack over earthquake, since it has a higher chance of fainting the other pokemon before you can faint yourself

#poke_id, attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types, status, stat_multipliers):
testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 90, 100, 90, 1.0, 1, ['quickattack', 'earthquake'], ['normal'], None, stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1.0, 1, ['tackle'], ['normal'], None, stat_multiplier)

action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print(testpoke1, testpoke2)
print("action is ", action) # favor earthquake over quickattack for raw DPS

#poke_id, attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types, status, stat_multipliers):
testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 110, 100, 90, 0.1, 1, ['quickattack', 'earthquake'], ['normal'], None, stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 0.1, 1, ['tackle'], ['normal'], None, stat_multiplier)

action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print(testpoke1, testpoke2)
print("action is ", action) # This time, we favor earthquake over quickattack even though we are at low hp, because we're faster

#poke_id, attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types, status, stat_multipliers):
testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 110, 100, 90, 0.1, 1, ['quickattack', 'earthquake'], ['normal'], None, stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 0.1, 1, ['tackle', 'quickattack'], ['normal'], None, stat_multiplier)

action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print(testpoke1, testpoke2)
print("action is ", action) # Now, we quickattack again, since they have quickattack as an option, and we don't want them to quickattack if we use earthquake

testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1.0, 1, ['swordsdance', 'slash'],['normal'], "None", stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1.0, 1, ['tackle'], ['normal'], "None", stat_multiplier)

print(testpoke1, testpoke2)
agent = pokemon_minimax.MinimaxAgent(depth=2) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # At depth 2, favour slash
agent = pokemon_minimax.MinimaxAgent(depth=3) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # at depth 3, favour swordsdance

testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1.0, 1, ['swordsdance', 'blizzard'],['normal'], "None", stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1.0, 1, ['tackle'], ['normal'], "None", stat_multiplier)

print(testpoke1, testpoke2)
agent = pokemon_minimax.MinimaxAgent(depth=2) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # At depth 2, favour slash
agent = pokemon_minimax.MinimaxAgent(depth=3) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # at depth 3, favour swordsdance

testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 0.1, 1, ['swordsdance', 'slash'],['normal'], "None", stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 0.1, 1, ['tackle'], ['normal'], "None", stat_multiplier)

print(testpoke1, testpoke2)
agent = pokemon_minimax.MinimaxAgent(depth=2) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # At depth 2, favour slash
agent = pokemon_minimax.MinimaxAgent(depth=3) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # at depth 3, favour swordsdance

testpoke1 = sim.Pokemon(1, 210, 166, 174, 174, 192, 276, 88, 1.0, 1, ['reflect', 'fireblast', 'flamethrower', 'bodyslam'],['fire'], "None", stat_multiplier)
testpoke2 = sim.Pokemon(1, 266, 244, 147, 147, 184, 234, 74, 1.0, 1, ['crabhammer', 'swordsdance', 'hyperbeam', 'bodyslam'], ['water'], "None", stat_multiplier)

print(testpoke1, testpoke2)
agent = pokemon_minimax.MinimaxAgent(depth=1) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)

testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1.0, 1, ['blizzard', 'blizzardnofreeze'],['water'], "None", stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1.0, 1, ['thunder'], ['normal'], "None", stat_multiplier)

print(testpoke1, testpoke2)
agent = pokemon_minimax.MinimaxAgent(depth=3) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # at depth 3, favour swordsdance

testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 0.1, 1, ['blizzard', 'blizzardnofreeze'],['water'], "None", stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 0.1, 1, ['thunder'], ['normal'], "None", stat_multiplier)

print(testpoke1, testpoke2)
agent = pokemon_minimax.MinimaxAgent(depth=3) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # at depth 3, favour swordsdance

testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1, 1, ['flamethrower', 'flamethrowernoburn'],['normal'], "None", stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1, 1, ['specialslash'], ['normal'], "None", stat_multiplier)

print(testpoke1, testpoke2)
agent = pokemon_minimax.MinimaxAgent(depth=3) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # at depth 3, favour swordsdance

testpoke1 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1, 1, ['flamethrower', 'flamethrowernoburn'],['normal'], "None", stat_multiplier)
testpoke2 = sim.Pokemon(1, 100, 100, 100, 100, 100, 100, 100, 1, 1, ['slash'], ['normal'], "None", stat_multiplier)

print(testpoke1, testpoke2)
agent = pokemon_minimax.MinimaxAgent(depth=3) #can specify search depth here
action = agent.getAction(curr_poke='1', team_poke={'1':testpoke1}, enemy_poke=testpoke2)
print("action is ", action) # at depth 3, favour swordsdance

#battle 2 vileplume vs snorlax

#battle 3 machamp vs snorlax


