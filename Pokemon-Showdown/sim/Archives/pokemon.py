import json
import sys

NUM_TEAM_MEMBERS = 6


class Pokemon:
  #currPokemon = None
  #theirPokemon = None
  #ourHP = []
  #theirHP = None
  #ourStatus = []
  #theirStatus = None
  #ourDmg = []
  #theirDmg = []

  def __init__(self, data):
    #print(data)
    self.data = data
    self.currPokemon = data['currPokemon']
    self.theirPokemon = data['theirPokemon']
    self.ourHP = data['ourHp']
    self.theirHP = data['theirHp']
    self.ourStatus = data['ourStatus']
    print("data given is ", self.ourStatus)
    self.theirStatus = data['theirStatus']
    self.ourDmg = data['ourDmg']
    self.theirDmg = data['theirDmg']
    self.fainted = data['fainted']

  def getLegalActions(self, agentIndex=0):
    """
    Returns the legal actions for the agent specified.
    """
    if self.isWin() or self.isLose():
      return []

    if agentIndex == 0:  
      return self.ourDmg
    else:
      return self.theirDmg 

  def getScore(self, agentIndex):
    teamScore = 0
    #if agentIndex == 0:
    for key, value in self.ourHP.items():  # need to define this
      #print(self.ourStatus)
      #print(self.ourHP)
      if self.ourStatus[str(key)]:
        status_effect = 0.5
      else:
        status_effect = 1
      teamScore += value * status_effect
    teamScore = teamScore / NUM_TEAM_MEMBERS
    if self.theirStatus:
      status_effect = 0.5
    else:
      status_effect = 1
    enemyScore = self.theirHP * status_effect
    score = teamScore - enemyScore
   #print(score)
    #print(self.ourDmg)
    #print(self.theirDmg)
    return score
    '''#else:
      /*if self.theirStatus:
        status_effect = 0.5
      else:
        status_effect = 1
      enemyScore = self.theirHP * status_effect
      if self.ourStatus[str(self.currPokemon)]:
        status_effect = 0.5
      else:
        status_effect = 1
      teamScore = self.ourHP[str(self.currPokemon)] * status_effect
      return enemyScore - teamScore'''

  def generateSuccessor(self, agentIndex, action):
    """
    Returns the successor state after the specified agent takes the action.
    """
    # Check that successors exist
    if self.isWin() or self.isLose():
      raise Exception('Can\'t generate a successor of a terminal state.')
    data = {}
    data['currPokemon'] = self.currPokemon 
    data['theirPokemon'] = self.theirPokemon 
    data['ourHp'] = self.ourHP 
    data['theirHp'] = self.theirHP 
    data['ourStatus'] = self.ourStatus 
    data['theirStatus'] =  self.theirStatus 
    data['ourDmg'] = self.ourDmg 
    data['theirDmg'] = self.theirDmg 
    data['fainted'] = self.fainted 

    poke = Pokemon(data)
   #print("Successor generated")
    # Let agent's logic deal with its action's effects on the board
    if agentIndex == 0:  # Pacman is moving
      self.applyAction(poke, agentIndex, action)
    else:                # A ghost is moving
      self.applyAction(poke, agentIndex, action)

    # Resolve multi-agent effects
    # Book keeping
    # compute score change from damage function
    return poke

  def applyAction(self, pokemon, agentIndex, action):
    if agentIndex == 0:
      if self.ourDmg[str(action)] == -1:
        self.theirStatus = True
        return 
      health = self.theirHP
      health -= self.ourDmg[str(action)]
      self.theirHP = health
    else:
      if self.theirDmg[str(action)] == -1:
        self.ourStatus[str(self.currPokemon)] = True
      return
      health = self.ourHP[str(self.currPokemon)]
      health -= self.theirDmg[str(action)]
      self.ourHP[self.currPokemon] = health

  def getLegalPlayerActions(self):
    return self.getLegalActions(0)

  def getLegalEnemyActions(self):
    return self.getLegalActions(1)

  def isLose(self):
    for key, value in self.ourHP.items():
      if value:
        return False
    return True
     # will need to define this

  def isWin(self):
    # will need to keep track of number of enemy opponents we have murked
    return self.theirHP == 0
