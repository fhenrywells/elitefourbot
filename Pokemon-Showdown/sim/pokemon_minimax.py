import itertools 


import pysim.pokemon as sim

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
			if sim.isWin(enemy_poke):
				return [], sim.getScore(team_poke, enemy_poke)
			if sim.isLose(team_poke):
				return [], sim.getScore(team_poke, enemy_poke)
			legalPlayerMoves = sim.getLegalTeamActions(curr_poke, team_poke)
			legalEnemyMoves = sim.getLegalEnemyActions(enemy_poke)
			if len(legalPlayerMoves) == 0 or len(legalEnemyMoves) == 0:
				return [], sim.getScore(team_poke, enemy_poke)
			if depth == 0:
				return [], sim.getScore(team_poke, enemy_poke)
			
			if player:
				nextPlayer = 0
			else:
				depth -=1
				nextPlayer = 1
			candidates = []

			action_pairs = list(
				itertools.product(legalPlayerMoves, legalEnemyMoves)) \
			+ list(itertools.product(legalEnemyMoves, legalPlayerMoves))

			'''action_pairs = list(list(zip(r, p)) for (r, p) in zip(
				repeat(legalPlayerMoves),
				permutations(legalEnemyMoves)))
			'''
			print("enemy attack is ", enemy_poke.attack)
			print("enemy defense is ", enemy_poke.defense)
			print("our attack is ", team_poke[curr_poke].attack)
			print("our defense is ", team_poke[curr_poke].defense)

			for pair in action_pairs:
				p1action = pair[0]
				p2action = pair[1]
				#print("p1action is {}, p2 action is {}".format(p1action, p2action))
				results = sim.performActions(
					team_poke[curr_poke],
					enemy_poke,
					p1action,
					p2action,
					team_poke
					)

				#print(results)
				#for result in results:
				#	score = result[0]*recurse(result[1][0],result[1][1])
				'''candidates.append((pair, recurse(sim.performActions(
					team_poke[curr_poke],
					enemy_poke,
					p1action,
					p2action,
					team_poke
					),
				depth,
				nextPlayer
				)))
				'''
				if player == 0:
					threshold = float('-inf')
					for candidate in candidates:
						if candidate[1] > threshold:
							threshold = candidate[1] #score
							action_pair = candidate[0] 
				else: #enemy
					threshold = float('+inf')
					for candidate in candidates:
						if candidate[1] < threshold:
							threshold = candidate[1]
							action_pair = candidate[0]
			return (action_pair, threshold)
		depth = self.depth
		player = self.index
		action, value = recurse(curr_poke, team_poke, enemy_poke, depth, player)
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