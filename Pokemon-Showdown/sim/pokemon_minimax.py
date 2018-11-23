#import pokemon

class Agent:
	"""
	An agent must define a getAction method, but may also define the
	following methods which will be called if they exist:

	def registerInitialState(self, state): # inspects the starting state
	"""
	def __init__(self, index=0):
		self.index = index

	def getAction(self, state):
		"""
		The Agent will receive a pokemon (from either {pacman, capture, sonar}.py) and
		must return an action from Directions.{North, South, East, West, Stop}
		"""
		raiseNotDefined()


class MultiAgentSearchAgent(Agent):
	"""
	"""

	def __init__(self, depth = '2'):
		self.index = 0 
		self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
	def getAction(self, pokemon):
		def recurse(pokemon, depth, player):
			legalMoves = pokemon.getLegalActions(player)
			if pokemon.isWin():
				return [], pokemon.getScore(self.index)
			if pokemon.isLose():
				return [], pokemon.getScore(self.index)
			if len(legalMoves) == 0:
				return [], pokemon.getScore(self.index)
			candidates = []
			if depth == 0:
				return [], pokemon.getScore(self.index)
			if player:
				nextPlayer = 0
			else:
				depth -=1
				nextPlayer = 1
			for action in legalMoves:
				candidates.append((action, recurse(pokemon.generateSuccessor(player, action), depth, nextPlayer)[1]))
				if player == 0: #pacman
					threshold = float('-inf')
					for candidate in candidates:
						if candidate[1] > threshold:
							threshold = candidate[1] #score
							action = candidate[0] #
				else: #enemy
					threshold = float('+inf')
					for candidate in candidates:
						if candidate[1] < threshold:
							threshold = candidate[1]
							action = candidate[0]
			return (action, threshold)
		depth = self.depth
		player = self.index
		action, value = recurse(pokemon, depth, player)
		index = 1
		print("action produced")
		for key in pokemon.ourDmg.keys():
			#print(action)
			print("key is {}, action is {}".format(key,action))
			if str(key) == str(action):
				return "move " + str(index)
			index +=1

		#return action 
		# END_YOUR_CODE