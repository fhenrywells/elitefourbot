import pickle
from collections import defaultdict

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

enemy_poke = pickle.load( open( "enemypoke.p", "rb" ) )
team_poke = pickle.load( open( "teampoke.p", "rb" ) )
curr_poke = "150"

#battle 1 scyther vs snorlax
agent = pokemon_minimax.MinimaxAgent() #can specify search depth here 

our_poke = team_poke[curr_poke]
action = agent.getAction(curr_poke=curr_poke, team_poke = team_poke, enemy_poke = enemy_poke)
#print("our moves are", team_poke[curr_poke].moveids)
print("Action is ", action)
 #return(action)


#battle 2 vileplume vs snorlax

#battle 3 machamp vs snorlax


