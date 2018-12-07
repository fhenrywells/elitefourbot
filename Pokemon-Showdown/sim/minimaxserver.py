import json
import logging
from pprint import pprint

from flask import Flask
from flask import request

import pokemon_minimax
import pysim.pokemon_simple as sim

app = Flask(__name__)


@app.route('/getaction', methods=['POST'])
def get_action():
    data = request.data
    dataDict = json.loads(data)
    pprint(dataDict)

    # Enemy Pokemon Info
    theirHp = float(dataDict['theirHp']) # theirHpStatus[0] is hp, [1] is status effect
    theirStatus = dataDict['theirStatus'] if dataDict['theirStatus'] != "False" else None
    # print("Their details are", dataDict["theirDetails"])
    # if "Mime" in dataDict["theirDetails"]:
    #  dataDict["theirDetails"].replace(" Mime", "Mime")

    # Our Team Info
    dataDict['ourMaxHp'] = {}
    dataDict['ourStatus'] = {}
    dataDict['ourLevel'] = {}
    # print("our hp is ", dataDict['ourHp'])
    for key, value in dataDict['ourHp'].items():
        if value != "0 fnt":
            ourHpStatus = dataDict['ourHp'][key].split(" ")
            if dataDict['ourHp'][key] == "0 fnt":
                dataDict['ourHp'][key] = 0.0
                continue
            if len(ourHpStatus) == 2:
                ourHp = ourHpStatus[0].split("/")
                dataDict['ourHp'][key] = float(ourHp[0]) / float(ourHp[1])
                dataDict['ourMaxHp'][key] = int(ourHp[1])
                dataDict['ourStatus'][key] = ourHpStatus[1]
            else:
                ourHp = ourHpStatus[0].split("/")
                dataDict['ourHp'][key] = float(ourHp[0]) / float(ourHp[1])
                dataDict['ourMaxHp'][key] = int(ourHp[1])
                dataDict['ourStatus'][key] = "None"
            # print("Our details are", dataDict["ourDetails"][key])
            # if "Mime" in dataDict["ourDetails"][key]:
            #  dataDict["ourDetails"][key].replace(" Mime", "Mime")
            ourLevelInfo = dataDict['ourDetails'][key].split(", ")
            dataDict["ourLevel"][key] = int(ourLevelInfo[1][1:])
            generation = int(dataDict['generation'][-1])

    # Temporary data containers for packing dataDict info

    pokemonTeam = {}
    # print("base stats are ", dataDict['ourBaseStats'])
    # print("max hp values: ",dataDict['ourMaxHp'])
    for key, value in dataDict['ourHp'].items():
        if value != "0 fnt":
            # print("max hp values: ",dataDict['ourMaxHp'])
            key = str(key)
            ourCurrStats = list(dataDict['ourStats'][key].values())
            # keyrint(dataDict['ourStatus'])
            # print("base stats are ", dataDict['ourBaseStats'])
            ourStatMultiplier = dataDict['ourBoosts']
            pokemonTeam[key] = (
                dataDict["ourPokemon"][key],
                ourCurrStats,
                dataDict['ourStats'][key]['hp'],
                dataDict['ourLevel'][key],
                dataDict['ourHp'][key],
                dataDict['ourMoves'][key],
                dataDict['ourTypes'][key],
                dataDict['ourStatus'][key],
                ourStatMultiplier
            )
    theirCurrStats = list(dataDict["theirBaseStats"].values())
    theirStatMultiplier = dataDict['theirBoosts']
    print("Team: ",pokemonTeam)
    enemy = (
        dataDict['theirPokemon'],
        theirCurrStats,
        dataDict['theirBaseStats']['hp'],
        dataDict["theirLevel"],
        dataDict['theirHp'],
        list(dataDict['theirMoves']),
        dataDict['theirTypes'],
        dataDict["theirStatus"],
        theirStatMultiplier
    )
    print("Enemy: ",enemy)
    team_poke = {}  # dictionary containing our team's pokemon objects
    # print("generation is ", type(generation))
    for p in pokemonTeam.keys():
        ally = pokemonTeam[p]
        team_poke[p] = sim.Pokemon(
            ally[0],
            ally[1][0],  # att
            ally[1][1],  # def
            ally[1][3],  # sp att
            ally[1][4],  # sp def
            ally[1][5],  # speed
            ally[1][2],  # max hp
            ally[3],  # level
            ally[4],  # curr hp
            generation,
            list(set(ally[5])),  # moves
            ally[6],  # types
            ally[7],  # status
            ally[8]  # stat multiplier
        )
        # print("Ally: ", ally)
    enemy_poke = sim.Pokemon(  # enemy pokemon object
        enemy[0],
        enemy[1][0],  # att
        enemy[1][1],  # def
        enemy[1][3],  # sp att
        enemy[1][4],  # sp def
        enemy[1][5],  # speed
        enemy[1][2],  # max hp
        enemy[3],  # level
        enemy[4],  # curr hp
        generation,
        list(set(enemy[5])),  # moves
        enemy[6],  # types
        enemy[7],  # status
        enemy[8]  # stat multiplier
    )
    # print("Enemy: ", enemy)
    curr_poke = str(dataDict["currPokemon"])  # current pokemon

    # recharging (deprecated, handled in battle-stream)
    # if len(team_poke[curr_poke].moveids) == 0:
    #  return ("move recharge")
    print(team_poke[curr_poke])
    print(enemy_poke)

    agent = pokemon_minimax.MinimaxAgent(depth=2)  # can specify search depth here
    action = agent.getAction(curr_poke=curr_poke, team_poke=team_poke, enemy_poke=enemy_poke)
    # print("our moves are", team_poke[curr_poke].moveids)
    # print("Action is ", action)
    print("ACTION IS: ", action)
    return (action)


if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(debug=True, host="127.0.0.1", port=5000)
