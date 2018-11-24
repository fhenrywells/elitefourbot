from flask import Flask
from flask import request
import pysim.sim_pokemon as sim
import pokemon_minimax
import json

app = Flask(__name__)


@app.route('/getaction', methods=['POST'])
def get_action():
  data = request.data
  dataDict = json.loads(data)
  theirHpStatus = dataDict['theirHp'].split(" ")
  
  #Enemy Pokemon Info
  if len(theirHpStatus) == 2:
    theirHp = theirHpStatus[0].split("/")
    dataDict['theirHp'] = float(theirHp[0]) / float(theirHp[1])
    dataDict['theirMaxHp'] = theirHp[1]
    dataDict['theirStatus'] = theirHpStatus[1]
  else:
    theirHp = theirHpStatus[0].split("/")
    dataDict['theirHp'] = float(theirHp[0]) / float(theirHp[1])
    dataDict['theirMaxHp'] = theirHp[1]
    dataDict['theirStatus'] = "None"
  theirLevelInfo = dataDict['theirDetails'].split(" ")
  dataDict["theirLevel"] = theirLevelInfo[1]

  #Our Team Info
  dataDict['ourMaxHp'] = {}
  dataDict['ourStatus'] = {}
  dataDict['ourLevel'] = {}
  for key in dataDict['ourHp'].keys():
    ourHpStatus = dataDict['ourHp'][key].split(" ")
    if dataDict['ourHp'][key] == "0 fnt":
      dataDict['ourHp'][key] = 0.0
      continue
    if len(theirHpStatus) == 2:
      ourHp = ourHpStatus[0].split("/")
      dataDict['ourHp'][key] = float(ourHp[0]) / float(ourHp[1])
      dataDict['ourMaxHp'][key] = ourHp[1]
      dataDict['ourStatus'][key] = ourHpStatus[1]   
    else:
      ourHp = ourHpStatus[0].split("/")
      dataDict['ourHp'][key] = float(ourHp[0]) / float(ourHp[1])
      dataDict['ourMaxHp'][key] = ourHp[1]
      dataDict['ourStatus'][key] = "None"
    ourLevelInfo = dataDict['ourDetails'][key].split(" ")
    dataDict["ourLevel"][key] = ourLevelInfo[1]
    generation = dataDict['generation'][-1:]

  #Temporary data containers for packing dataDict info






  pokemonTeam = {}
  for p in dataDict['ourHp'].keys():
    p = str(p)
    ourCurrStats = list(dataDict['ourStats'][p].values())                      
    #print(dataDict['ourStatus'])
    ourBaseStats = list(dataDict['ourBaseStats'][p].values())
    ourStatMultiplier = {}
    for i in range(len(ourCurrStats)):
      ourStatMultiplier[i] = float(ourCurrStats[i])/float(ourBaseStats[i])
    pokemonTeam[p] = (
                      dataDict["ourPokemon"][p],
                      ourCurrStats,
                      dataDict['ourMaxHp'][p],                      
                      dataDict['ourLevel'][p],
                      dataDict['ourHp'][p],
                      dataDict['ourMoves'][p],
                      dataDict['ourTypes'][p],
                      dataDict['ourStatus'][p],
                      ourStatMultiplier
                      )
  #print("Team: ", pokemonTeam)

  theirCurrStats = list(dataDict["theirStats"].values())
  theirBaseStats = list(dataDict["theirBaseStats"][str(dataDict['theirPokemon'])].values())
  theirStatMultiplier = {}
  for i in range(len(theirCurrStats)):
    theirStatMultiplier[i] = float(theirCurrStats[i])/float(theirBaseStats[i])

  print(pokemonTeam)
  enemy = (
          dataDict['theirPokemon'],
          theirCurrStats,
          dataDict['theirMaxHp'], 
          dataDict["theirLevel"],
          dataDict['theirHp'],
          list(dataDict['theirMoves']),
          dataDict['ourTypes'],
          dataDict["theirStatus"],
          theirStatMultiplier
          )
  print(enemy)
  team_poke = {} #dictionary containing our team's pokemon objects
  for p in pokemonTeam.keys():
    ally = pokemonTeam[p]
    team_poke[p] = sim.Pokemon(
      ally[0],
      ally[1][0], #att
      ally[1][1], #def
      ally[1][2], #sp att
      ally[1][3], #sp def
      ally[1][4], #speed
      ally[2], #max hp
      ally[3], #level
      ally[4], #curr hp
      generation,
      ally[5], #moves
      ally[6], # types
      ally[7], # status
      ally[8] # stat multiplier
    )

  enemy_poke = sim.Pokemon( #enemy pokemon object
    enemy[0],
    enemy[1][0], #att
    enemy[1][1], #def
    enemy[1][2], #sp att
    enemy[1][3], #sp def
    enemy[1][4], #speed
    enemy[2], #max hp
    enemy[3], #level
    enemy[4], #curr hp
    generation,
    enemy[5], #moves
    enemy[6], # types
    enemy[7], # status
    enemy[8] # stat multiplier
    )
  curr_poke = dataDict["currPokemon"] #current pokemon 

  agent = pokemon_minimax.MinimaxAgent() #can specify search depth here 
  action = agent.getAction(curr_poke=curr_poke, team_poke = team_poke, enemy_poke = enemy_poke)
  #print("Action is ", action)
  return(action)


if __name__ == '__main__':
  app.run(debug=True, host="127.0.0.1", port=5000)
