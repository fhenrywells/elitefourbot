import itertools 
import copy

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

	def __init__(self, depth = '2'):
		self.index = 0 
		self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
	def getAction(self, curr_poke, team_poke, enemy_poke,):
		def recurse(curr_poke, team_poke, enemy_poke, depth, player):
			print("player is minotaur ", player)
			if sim.isWin(enemy_poke):
				return [], sim.getScore(team_poke, enemy_poke)
			if sim.isLose(team_poke):
				return [], sim.getScore(team_poke, enemy_poke)
			legalPlayerMoves = sim.getLegalTeamActions(curr_poke, team_poke)
			legalEnemyMoves = sim.getLegalEnemyActions(enemy_poke)

			print("depth is ", depth)
			if len(legalPlayerMoves) == 0 or len(legalEnemyMoves) == 0:
				return [], sim.getScore(team_poke, enemy_poke)
			if depth == 0:
				return [], sim.getScore(team_poke, enemy_poke)
			if player:
				nextPlayer = 0
			else:
				depth -= 1
				nextPlayer = 1
			candidates = []
			action_pairs = list(
				itertools.product(legalPlayerMoves, legalEnemyMoves)) 
			for pair in action_pairs:
				p1action = pair[0]
				p2action = pair[1]
				#print("p1action is {}, p2 action is {}".format(p1action, p2action))
				results = sim.performActions(
					team_poke[curr_poke],
					enemy_poke,
					p1action,
					p2action,
					)
				#print(results)
				score = 0
				print("results are ", results)
				for result in results:

					new_team_poke = copy.deepcopy(team_poke)
					new_team_poke[pair[0][1].poke_id if pair[0][0] == "switch" else curr_poke] = result[1][0]
					rec = recurse(result[1][0].poke_id, new_team_poke, result[1][1], depth, nextPlayer)
					score += result[0] * rec[1]
				candidates.append((pair, score))
				print("candidates purple are ", candidates)
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
			return (action_pair, threshold) #bug is around here, need to know when to return the value properly


		depth = self.depth
		player = self.index
		print("player is ", player)
		action, value = recurse(curr_poke, team_poke, enemy_poke, depth, player)
		index = 1
		print("action produced: ", action)
		return "move " + action[0][1]
		if type(action[0][1]) is str:
			if player == 0:
				for move in team_poke[curr_poke].moveids:
					print(move)
					if str(move) == str(action[0][1]):
						print("do we get here")
						val = ("move " + str(index + 1))
						print(val)
						return val
					index += 1
		else:
			print("Team poke is ", team_poke)
			for poke in team_poke:
				print("poke is ", poke)
				if poke == action[0][1].poke_id:
					return ("switch " + str(index))


