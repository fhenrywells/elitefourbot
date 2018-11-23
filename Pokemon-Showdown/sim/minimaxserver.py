from flask import Flask
from flask import request
#import sim_pokemon
import pokemon_minimax
import json

app = Flask(__name__)


@app.route('/getaction', methods=['POST'])
def get_action():
  data = request.data
  dataDict = json.loads(data)
  theirHpStatus = dataDict['theirHp'].split(" ")
  print(dataDict)
  
  if len(theirHpStatus) == 2:
    theirHp = theirHpStatus[0].split("/")
    dataDict['theirHp'] = float(theirHp[0]) / float(theirHp[1])
    dataDict['theirStatus'] = theirHpStatus[1]
  else:
    theirHp = theirHpStatus[0].split("/")
    dataDict['theirHp'] = float(theirHp[0]) / float(theirHp[1])
    dataDict['theirStatus'] = "None"

  dataDict['ourStatus'] = {}
  for key in dataDict['ourHp'].keys():
    ourHpStatus = dataDict['ourHp'][key].split(" ")
    if dataDict['ourHp'][key] == "0 fnt":
      dataDict['ourHp'][key] = 0.0
      continue
    if len(theirHpStatus) == 2:
      ourHp = ourHpStatus[0].split("/")
      dataDict['ourHp'][key] = float(ourHp[0]) / float(ourHp[1])
      dataDict['ourStatus'][key] = ourHpStatus[1]   
    else:
      ourHp = ourHpStatus[0].split("/")
      dataDict['ourHp'][key] = float(ourHp[0]) / float(ourHp[1])
      dataDict['ourStatus'][key] = "None"
  #print(dataDict)
  
  #poke = pokemon.Pokemon(dataDict)
  #print(pokemon)
  #print(dataDict['ourMoves'])
  #for key,value in dataDict['ourMoves'].items():
  #  print(value)
  #  print(type(value))
  pokemonTeam = {}
  for p in dataDict['ourHp'].keys():
    p = str(p)
    print(dataDict['ourStatus'])
    pokemonTeam[p] = (
                      dataDict['ourMoves'][p],
                      dataDict['ourHp'][p],
                      dataDict['ourStatus'][p],
                      dataDict['ourStats'][p]
                      )
  print("Team: ", pokemonTeam)
  currPokemon = dataDict['currPokemon']
  print("Current: ", currPokemon)
  enemy = (dataDict['theirPokemon'],
          dataDict['theirHp'],
          dataDict["theirStatus"],
          dataDict["theirStats"]
          )
  print("Enemy: ", enemy)

  #gameState = pokemon.GameState()
  agent = pokemon_minimax.MinimaxAgent()

  #action = agent.getAction(pokemon=poke)
  #print("Action is ", action)
  return(action)


if __name__ == '__main__':
  app.run(debug=True, host="127.0.0.1", port=5000)
