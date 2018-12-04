import json
import logging

from flask import Flask
from flask import request

import pokemon_minimax
import pysim.pokemon_simple as sim

app = Flask(__name__)


@app.route('/getaction', methods=['POST'])
def get_action():
    data = request.data
    dataDict = json.loads(data)
    theirHpStatus = dataDict['theirHp'].split(" ") # theirHpStatus[0] is hp, [1] is status effect

    # Enemy Pokemon Info
    if len(theirHpStatus) == 2:
        theirHp = theirHpStatus[0].split("/")
        dataDict['theirHp'] = float(theirHp[0]) / float(theirHp[1])
        dataDict['theirMaxHp'] = int(theirHp[1])
        dataDict['theirStatus'] = theirHpStatus[1]
    else:
        theirHp = theirHpStatus[0].split("/")
        dataDict['theirHp'] = float(theirHp[0]) / float(theirHp[1])
        dataDict['theirMaxHp'] = int(theirHp[1])
        dataDict['theirStatus'] = "None"
    # print("Their details are", dataDict["theirDetails"])
    # if "Mime" in dataDict["theirDetails"]:
    #  dataDict["theirDetails"].replace(" Mime", "Mime")
    theirLevelInfo = dataDict['theirDetails'].split(", ")
    dataDict["theirLevel"] = int(theirLevelInfo[1][1:])

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
            ourBaseStats = list(dataDict['ourBaseStats'][key].values())
            ourStatMultiplier = {}
            for i in range(len(dataDict["ourTypes"][key])):
                dataDict["ourTypes"][key][i] = dataDict["ourTypes"][key][i].lower()
            for i in range(len(ourCurrStats)):
                ourStatMultiplier[i] = float(ourCurrStats[i]) / float(ourBaseStats[i])
            pokemonTeam[key] = (
                dataDict["ourPokemon"][key],
                ourCurrStats,
                dataDict['ourMaxHp'][key],
                dataDict['ourLevel'][key],
                dataDict['ourHp'][key],
                dataDict['ourMoves'][key],
                dataDict['ourTypes'][key],
                dataDict['ourStatus'][key],
                ourStatMultiplier
            )
    theirCurrStats = list(dataDict["theirStats"].values())
    theirBaseStats = list(dataDict["theirBaseStats"][str(dataDict['theirPokemon'])].values())
    theirStatMultiplier = {}
    for i in range(len(dataDict["theirTypes"])):
        dataDict["theirTypes"][i] = dataDict["theirTypes"][i].lower()
    for i in range(len(theirCurrStats)):
        theirStatMultiplier[i] = float(theirCurrStats[i]) / float(theirBaseStats[i])

    # print("Team: ",pokemonTeam)
    enemy = (
        dataDict['theirPokemon'],
        theirCurrStats,
        dataDict['theirMaxHp'],
        dataDict["theirLevel"],
        dataDict['theirHp'],
        list(dataDict['theirMoves']),
        dataDict['theirTypes'],
        dataDict["theirStatus"],
        theirStatMultiplier
    )
    # print("Enemy: ",enemy)
    team_poke = {}  # dictionary containing our team's pokemon objects
    # print("generation is ", type(generation))
    for p in pokemonTeam.keys():
        ally = pokemonTeam[p]
        team_poke[p] = sim.Pokemon(
            ally[0],
            ally[1][0],  # att
            ally[1][1],  # def
            ally[1][2],  # sp att
            ally[1][3],  # sp def
            ally[1][4],  # speed
            ally[2],  # max hp
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
        enemy[1][2],  # sp att
        enemy[1][3],  # sp def
        enemy[1][4],  # speed
        enemy[2],  # max hp
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

    agent = pokemon_minimax.MinimaxAgent(depth=3)  # can specify search depth here
    action = agent.getAction(curr_poke=curr_poke, team_poke=team_poke, enemy_poke=enemy_poke)
    # print("our moves are", team_poke[curr_poke].moveids)
    # print("Action is ", action)
    print("Action is", action)
    return (action)


if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(debug=True, host="127.0.0.1", port=5000)
