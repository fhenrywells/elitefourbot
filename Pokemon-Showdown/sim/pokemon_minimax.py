import pysim.sim_pokemon as sim

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

	def __init__(self, depth = '3'):
		self.index = 0 
		self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
	def getAction(self, curr_poke, team_poke, enemy_poke,):
		def recurse(curr_poke, team_poke, enemy_poke, depth, player):
			if sim.isWin():
				return [], sim.getScore(self.index)
			if sim.isLose():
				return [], sim.getScore(self.index)
			if len(legalMoves) == 0:
				return [], sim.getScore(self.index)

			legalPlayerMoves = sim.getLegalTeamActions(curr_poke, team_poke)
			legalEnemyMoves = sim.getLegalEnemyActions(enemy_poke)
			if depth == 0:
				return [], sim.getScore(self.index)
			if player:
				nextPlayer = 0
			else:
				depth -=1
				nextPlayer = 1
			candidates = []
			for p1action in legalPlayerMoves:
				for p2action in legalEnemyMoves:
					candidates.append((action, recurse(sim.performActions(
						team_poke[curr_poke],
						enemy_poke,
						p1action,
						p2action,
						team_poke
						),
					depth,
					nextPlayer
					)))
				if player == 0:
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
		action, value = recurse(curr_poke, team_poke, enemy_poke, depth, player)
		index = 1
		print("action produced")
		#for key in pokemon.ourDmg.keys():
			#print(action)
			print("key is {}, action is {}".format(key,action))
			if str(key) == str(action):
				return "move " + str(index)
			index +=1

		#return action 
		# END_YOUR_CODE