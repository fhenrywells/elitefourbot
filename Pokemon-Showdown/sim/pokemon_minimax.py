import copy
import itertools
import pickle
import sys
from collections import defaultdict

import pysim.pokemon_simple as sim

#states = defaultdict(list)


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

    def __init__(self, depth=2):
        self.index = 0
        self.depth = depth


class MinimaxAgent(MultiAgentSearchAgent):
    def getAction(self, curr_poke, team_poke, enemy_poke, ):
        #global states
        #states = defaultdict(list)
        #print(sim.getLegalTeamActions(curr_poke, team_poke))

        def recurse(curr_poke, team_poke, enemy_poke, depth, player, runningmovelist=[]):
            #global states
            # print("player is minotaur ", player)
            if sim.isWin(enemy_poke) or sim.isLose(team_poke) or depth == 0:
                #print(runningmovelist, sim.getScore(team_poke, enemy_poke))
                return [], sim.getScore(team_poke, enemy_poke)
            legalPlayerMoves = sim.getLegalTeamActions(curr_poke, team_poke)
            legalEnemyMoves = sim.getLegalEnemyActions(enemy_poke)

            depth -= 1

            max_our_move = None
            max_our_score = None
            for our_move in legalPlayerMoves:
                min_their_move = None
                min_their_score = None
                for their_move in legalEnemyMoves:
                    results = sim.performActions(
                        team_poke[curr_poke],
                        enemy_poke,
                        our_move,
                        their_move
                    )
                    new_team_poke = copy.deepcopy(team_poke)
                    new_team_poke[our_move[1].poke_id if our_move[0] == "switch" else curr_poke] = results[0][1][0]
                    newrunningmovelist = runningmovelist
                    #newrunningmovelist = copy.deepcopy(runningmovelist)
                    #newrunningmovelist.append((our_move, their_move))
                    score = \
                    recurse(results[0][1][0].poke_id, new_team_poke, results[0][1][1], depth, player, newrunningmovelist)[
                        1]
                    #states[depth].append((our_move, their_move))
                    if min_their_score is None or score < min_their_score:
                        min_their_score = score
                        min_their_move = their_move
                if max_our_score is None or min_their_score > max_our_score:
                    max_our_score = min_their_score
                    max_our_move = our_move
            return (max_our_move, min_their_move), max_our_score

        def recursealphabeta(curr_poke, team_poke, enemy_poke, depth, player, runningmovelist=[], alpha = float("-inf"), beta = float("+inf")):
            #global states
            # print("player is minotaur ", player)
            if sim.isWin(enemy_poke) or sim.isLose(team_poke) or depth == 0:
                # print(runningmovelist, sim.getScore(team_poke, enemy_poke))
                return [], sim.getScore(team_poke, enemy_poke)
            legalPlayerMoves = sim.getLegalTeamActions(curr_poke, team_poke)
            legalEnemyMoves = sim.getLegalEnemyActions(enemy_poke)

            depth -= 1

            max_our_move = None
            max_our_score = None
            for our_move in legalPlayerMoves:
                min_their_move = None
                min_their_score = None
                for their_move in legalEnemyMoves:
                    results = sim.performActions(
                        team_poke[curr_poke],
                        enemy_poke,
                        our_move,
                        their_move
                    )
                    new_team_poke = copy.deepcopy(team_poke)
                    new_team_poke[our_move[1].poke_id if our_move[0] == "switch" else curr_poke] = results[0][1][0]
                    #newrunningmovelist = copy.deepcopy(runningmovelist)
                    #newrunningmovelist.append((our_move, their_move))
                    score = \
                        recursealphabeta(results[0][1][0].poke_id, new_team_poke, results[0][1][1], depth, player, runningmovelist, alpha, beta)[
                            1]
                    #states[depth].append((our_move, their_move))
                    if min_their_score is None or score < min_their_score:
                        min_their_score = score
                        min_their_move = their_move
                    beta = min(score, beta)
                    if alpha >= beta:
                        break
                if max_our_score is None or min_their_score > max_our_score:
                    max_our_score = min_their_score
                    max_our_move = our_move
                alpha = max(min_their_score, alpha)
                if alpha >= beta:
                    break
            return (max_our_move, min_their_move), max_our_score

        depth = self.depth
        player = self.index
        # print("player is ", player)
        action, value = recurse(curr_poke, team_poke, enemy_poke, depth, player)
        index = 1
        # print("action produced: ", action)
        #print("move " + action[0][1])

        #for key, value in states.items():
        #    print("depth: {}, num states {}".format(key, len(value)))
        # print(json.dumps(json.loads(jsonpickle.encode(states)), indent=2))
        # print("states are ", states)
        return "move " + action[0][1]

        if type(action[0][1]) is str:
            if player == 0:
                for move in team_poke[curr_poke].moveids:
                    print(move)
                    if str(move) == str(action[0][1]):
                        # print("do we get here")
                        val = ("move " + str(index + 1))
                        print(val)
                        return val
                    index += 1
        else:
            # print("Team poke is ", team_poke)
            for poke in team_poke:
                # print("poke is ", poke)
                if poke == action[0][1].poke_id:
                    return ("switch " + str(index))
