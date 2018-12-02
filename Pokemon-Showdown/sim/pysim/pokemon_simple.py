import copy
import csv
import json
import jsonpickle
import os

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

move_effectiveness = {}
viable_moves = {}
NUM_TEAM_MEMBERS = 6

class Pokemon:
    _attack = None
    _defense = None
    _sp_att = None  # sp_att is used as special for gen1 pokemon
    _sp_def = None
    _speed = None
    maxhp = None
    level = None
    currhp = 1.0
    gen = None
    moveids = []
    types = []
    stat_multipliers = None 

    status = {"brn":0, "frz":0, "par":0, "psn":0, "slp":0, "tox":0}

    atk_stage = [0, 0]
    def_stage = [0, 0]
    spa_stage = [0, 0]
    spd_stage = [0, 0]
    spe_stage = [0, 0]

    #_tox_stage = 1

    def __init__(self, poke_id, attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types, status, stat_multipliers):
        self.poke_id = str(poke_id)
        self._attack = attack
        self._defense = defense
        self._sp_att = sp_att
        self._sp_def = sp_def
        self._speed = speed
        self.maxhp = maxhp
        self.level = level
        self.currhp = currhp
        self.gen = gen
        self.moveids = moveids
        self.types = types
        self.stat_multipliers = stat_multipliers
        if status is not None:
            self.status[status] = 1.0
        atk_stage = list(stat_multipliers.values())[0] - 1
        def_stage = list(stat_multipliers.values())[1] - 1
        spa_stage = list(stat_multipliers.values())[2] - 1
        spd_stage = list(stat_multipliers.values())[3] - 1
        spe_stage = list(stat_multipliers.values())[4] - 1
        self.atk_stage = [max(0, atk_stage), min(0, atk_stage)]
        self.def_stage = [max(0, def_stage), min(0, def_stage)]
        self.spa_stage = [max(0, spa_stage), min(0, spa_stage)]
        self.spd_stage = [max(0, spd_stage), min(0, spd_stage)]
        self.spe_stage = [max(0, spe_stage), min(0, spe_stage)]
        #self._tox_stage = _tox_stage

    def stage_to_multiplier(self, stage):
        return max(2, 2 + stage[0]) / max(2, 2 - stage[1])

    def handle_status(self):
        '''
        Handles status effects in place. Run on the Pokemon instance after performing actions.
        :return:
        '''
        for status, val in self.status.items():
            if status == "brn":
                self.currhp -= 1.0/16.0 * val
            elif status == "frz":
                pass
            elif status == "par":
                pass
            elif status == "psn" or self.status == "tox": # will need to be changed to account for tox
                self.currhp -= 1.0/16.0 * val # for gen1 will need to be changed for future gens
            elif self.status == "slp":
                pass
        #elif self.status == "tox":
           #self.currhp -= self._tox_stage/16.0
            #self._tox_stage += 1

    @property
    def attack(self):
        return int(self._attack * self.stage_to_multiplier(self.atk_stage) * (1 - 0.5 * self.status['brn']))

    @property
    def defense(self):
        return int(self._defense * self.stage_to_multiplier(self.def_stage))

    @property
    def sp_att(self):
        return int(self._sp_att * self.stage_to_multiplier(self.spa_stage))

    @property
    def sp_def(self):
        return int(self._sp_def * self.stage_to_multiplier(self.spd_stage))

    @property
    def speed(self):
        return int(self._speed * self.stage_to_multiplier(self.spe_stage) * (1 - 0.25 * self.status['par']))


def calcDamage(attackingPokemon, defendingPokemon, move):
    if attackingPokemon.gen == 1:
        critchance = attackingPokemon.speed / 512 * 8 ** (move.critratio - 1)
        #print("level is ", attackingPokemon.level)
        level = attackingPokemon.level
        level = level * (1 * (
            1 - critchance) + 2 * critchance)  # Expected value for level, taking into account crit chance
        #print("defendingPokemon is ", defendingPokemon)
        #print("def types are ", defendingPokemon.types)
        #print("effectiveness keys are ",move_effectiveness.keys())
        effectivenesses = [move_effectiveness[(
            move.type, def_type)] for def_type in defendingPokemon.types]
        effectiveness = 1
        for e in effectivenesses:
            effectiveness = effectiveness * e
        stab = 1.5 if move.type in attackingPokemon.types else 1
        modifier = stab * effectiveness

        #print("speed stages are ", defendingPokemon.spe_stage, attackingPokemon.spe_stage)
        #print("spa stages are ", defendingPokemon.spa_stage, attackingPokemon.spa_stage)
        #print("defending pokemon stats: {}, {}, {}, {}, {}".format(
        #    defendingPokemon.attack, defendingPokemon.defense,
        #    defendingPokemon.sp_att, defendingPokemon.sp_def,
        #    defendingPokemon.speed))
        #print("attacking pokemon stats: {}, {}, {}, {}, {}".format(
        #    attackingPokemon.attack, attackingPokemon.defense,
        #    attackingPokemon.sp_att, attackingPokemon.sp_def,
        #    attackingPokemon.speed))

        if move.category.lower() == "physical":
            a = attackingPokemon.attack
            d = defendingPokemon.defense
        else:
            a = attackingPokemon.sp_att
            d = defendingPokemon.sp_att
        basedmg = int(int(int(2 * level / 5 + 2) *
                          move.basePower * a / d) / 50 + 2)
        # Proper way to do it, uncomment for increased accuracy
        #random = list(range(217, 256))  # all random values
        #damage_values = [int(basedmg * modifier * r / 255.0) for r in random]
        #dam = sum(damage_values) / len(damage_values)
        # Fast way to do it
        dam = 236.0 / 255.0 * basedmg * modifier
        return dam
    else:
        raise (NotImplementedError(
            "Generation {} not implemented yet".format(attackingPokemon.gen)))


def performActions(p1_pokemon, p2_pokemon, p1action, p2action):
    ret = []
    #print("p1_pokemon is {}, p2_pokemon is {}".format(p1_pokemon, p2_pokemon))
    # switch first
    if p1action[0] == "switch" and p2action[0] == "switch":
        return [(1.0, (copy.copy(p1action[1]), copy.copy(p2action[1])))]
    if p1action[0] == "switch" and p2action[0] == "move":
        p1_pokemon = p1action[1]
        # Switch results, because returned states are from pokemon2's perspective
        p2_move_results = viable_moves[p2action[1]].effect(p2_pokemon, p1_pokemon)
        ret = [(prob, (poke_1, poke_2)) for prob, (poke_2, poke_1) in p2_move_results]
    if p2action[0] == "switch" and p1action[0] == "move":
        p2_pokemon = p2action[1]
        ret = viable_moves[p1action[1]].effect(p1_pokemon, p2_pokemon)

    if p1action[0] == "move" and p2action[0] == "move":
        p1move = viable_moves[p1action[1]]
        p2move = viable_moves[p2action[1]]
        # First, compare priorities
        if p1move.priority != p2move.priority:
            if p1move.priority > p2move.priority:
                p1_move_results = p1move.effect(p1_pokemon, p2_pokemon)
                for prob, (p1_poke, p2_poke) in p1_move_results:
                    p2_move_results = p2move.effect(p2_poke, p1_poke)
                    ret = ret + [(prob * newprob, (p1_poke_final, p2_poke_final))
                                 for newprob, (p2_poke_final, p1_poke_final) in p2_move_results]
            else:
                p2_move_results = p2move.effect(p2_pokemon, p1_pokemon)
                for prob, (p2_poke, p1_poke) in p2_move_results:
                    p1_move_results = p1move.effect(p1_poke, p2_poke)
                    ret = ret + [(prob * newprob, (p1_poke_final, p2_poke_final))
                                 for newprob, (p1_poke_final, p2_poke_final) in p1_move_results]

        # Then, compare speeds
        else:
            if p1_pokemon.speed > p2_pokemon.speed:
                p1_move_results = p1move.effect(p1_pokemon, p2_pokemon)
                for prob, (p1_poke, p2_poke) in p1_move_results:
                    p2_move_results = p2move.effect(p2_poke, p1_poke)
                    ret = ret + [(prob * newprob, (p1_poke_final, p2_poke_final))
                                 for newprob, (p2_poke_final, p1_poke_final) in p2_move_results]
            else:
                p2_move_results = p2move.effect(p2_pokemon, p1_pokemon)
                #print(p2_move_results)
                for prob, (p2_poke, p1_poke) in p2_move_results:
                    p1_move_results = p1move.effect(p1_poke, p2_poke)
                    ret = ret + [(prob * newprob, (p1_poke_final, p2_poke_final))
                                 for newprob, (p1_poke_final, p2_poke_final) in p1_move_results]

    for prob, (poke_1, poke_2) in ret:
        poke_1.handle_status()
        poke_2.handle_status()
    return ret


class Move:
    accuracy = None
    basePower = None
    category = None
    multihit = None
    pp = None
    priority = None
    secondary = None
    type = None
    boosts = None
    status = None
    effect = None
    critratio = None

    def __init__(self, movedata):
        self.accuracy = movedata['accuracy']
        self.basePower = movedata['basePower']
        self.category = movedata['category'].lower()
        self.multihit = movedata.get('multihit', 1)
        self.pp = movedata['pp']
        self.priority = movedata['priority']
        self.secondary = movedata['secondary']
        self.type = movedata['type'].lower()
        self.boosts = movedata.get('boosts', None)
        self.status = movedata.get('status', None)
        self.effect = getattr(self, movedata['id'], self.defaultmove)
        self.critratio = movedata.get('critratio', 1)

    def defaultmove(self, ourPokemon, theirPokemon):
        """
        Return a list of (prob, (poke1, poke2)) tuples resulting from taking this move
        :param ourPokemon:
        :param theirPokemon:
        :return:
        """
        # Copy pokemon for the new state
        ourPokemon_new = copy.copy(ourPokemon)
        theirPokemon_new = copy.copy(theirPokemon)
        '''print("orig Stats are ",
                "att: {}",
                "def: {}",
                "spa: {}",
                "spd: {}",
                "spe: {}".format(
                    theirPokemon.attack,
                    theirPokemon.defense,
                    theirPokemon.sp_att,
                    theirPokemon.sp_def,
                    theirPokemon.speed))
        '''
        states = []
        #print("our pokemon hit is ", ourPokemon_hit)
        # Add missed state first, if accuracy is <100
        if self.accuracy is True:
            acc = 1.0
        else:
            acc = self.accuracy / 100.0

        # Handle paralysis
        acc *= 1 - ourPokemon_new.status['par'] * 0.25
        acc *= 1 - ourPokemon_new.status['slp']

        # Do damage calc first
        if self.basePower != 0:
            damage = calcDamage(ourPokemon_new, theirPokemon_new, self)
            theirPokemon_new.currhp -= damage / theirPokemon_new.maxhp * acc

        # Then apply boosts if they exist
        if self.boosts is not None:
            # Apply boost to self
            if self.accuracy is True:
                ourPokemon_new.atk_stage[0] = min(6, self.boosts.get("atk", 0) + ourPokemon_new.atk_stage[0])
                ourPokemon_new.def_stage[0] = min(6, self.boosts.get("def", 0) + ourPokemon_new.def_stage[0])
                ourPokemon_new.spa_stage[0] = min(6, self.boosts.get("spa", 0) + ourPokemon_new.spa_stage[0])
                ourPokemon_new.spe_stage[0] = min(6, self.boosts.get("spe", 0) + ourPokemon_new.spe_stage[0])
            # Otherwise, apply boosts to opponent
            else:
                theirPokemon_new.atk_stage[1] = max(-6, self.boosts.get("atk", 0) * acc + theirPokemon_new.atk_stage[1])
                theirPokemon_new.def_stage[1] = max(-6, self.boosts.get("def", 0) * acc + theirPokemon_new.def_stage[1])
                theirPokemon_new.spa_stage[1] = max(-6, self.boosts.get("spa", 0) * acc + theirPokemon_new.spa_stage[1])
                theirPokemon_new.spe_stage[1] = max(-6, self.boosts.get("spe", 0) * acc + theirPokemon_new.spe_stage[1])

        # Apply status effect if there is one
        #print("their pokemon hit is ", theirPokemon_hit)
        if self.status is not None and theirPokemon_new.status is None:
            # Except fire-type moves can't burn fire-type pokemon
            if not (self.status == "brn" and self.type == "fire" and "fire" in theirPokemon.types):
                theirPokemon_new.status[self.status] += acc * (1 - sum(theirPokemon_new.status.keys()))
                #theirPokemon_hit._tox_stage = 1

        # If their Pokemon is frozen and this is a physical fire-type move that can burn, unfreeze them
        if theirPokemon_new.status == "frz" and self.type == "fire" and self.status == "brn" and self.category == "physical":
            theirPokemon_new.status['brn'] *= 1 - acc

        # Then, apply secondary effects if they exist
        if self.secondary is not None:
            secondary_acc = self.secondary['chance'] / 100.0 * acc
            if "status" in self.secondary.keys():
                theirPokemon_new.status[self.secondary['status']] += secondary_acc * (1 - sum(theirPokemon_new.status.values()))
            if "boosts" in self.secondary.keys():
                '''print("Stats are ",
                    "att: {}",
                    "def: {}",
                    "spa: {}",
                    "spd: {}",
                    "spe: {}".format(
                        theirPokemon_secondary.attack,
                        theirPokemon_secondary.defense,
                        theirPokemon_secondary.sp_att,
                        theirPokemon_secondary.sp_def,
                        theirPokemon_secondary.speed))'''
                theirPokemon_new.atk_stage[1] = max(-6, self.secondary['boosts'].get("atk", 0) * secondary_acc + theirPokemon_new.atk_stage[1])
                theirPokemon_new.def_stage[1] = max(-6, self.secondary['boosts'].get("def", 0) * secondary_acc + theirPokemon_new.def_stage[1])
                theirPokemon_new.spa_stage[1] = max(-6, self.secondary['boosts'].get("spa", 0) * secondary_acc + theirPokemon_new.spa_stage[1])
                theirPokemon_new.spe_stage[1] = max(-6, self.secondary['boosts'].get("spe", 0) * secondary_acc + theirPokemon_new.spe_stage[1])

        return [(1.0, (ourPokemon_new, theirPokemon_new))]

    def bide(self, ourPokemon, theirPokemon):
        #print("bide")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]

    def counter(self, ourPokemon, theirPokemon):
        #print("counter")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]

    def reflect(self, ourPokemon, theirPokemon):
        #print("reflect")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]

    def substitute(self, ourPokemon, theirPokemon):
        #print("substitute")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]


with open(dir_path + '/viablemovesdata.json') as f:
    move_data = json.loads(f.read())
    for id, data in move_data.items():
        viable_moves[id] = Move(data)

with open(dir_path + '/effectiveness.csv', 'rt') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        move_effectiveness[(row[0], row[1])] = float(row[2])


def getLegalTeamActions(curr_poke, team_poke):
    actions = []
    #print("curr poke unicorn is ", curr_poke)
    #print("team is ", team_poke)
    #print("curr poke is ", curr_poke)
    #print("move array is ", team_poke[curr_poke].moveids)
    for move in team_poke[curr_poke].moveids:
        #print("move is ", move)
        actions.append(("move", move))
    #for poke_id, pokemon in team_poke.items():
    #    if poke_id != curr_poke and pokemon.currhp > 0:
    #        actions.append(("switch", team_poke[poke_id]))
    #print("legal actions are ",actions)
    return actions

def getLegalEnemyActions(enemy_poke):
    actions = []
    for move in enemy_poke.moveids:
        actions.append(("move", move))
    return actions

def getScore(ourPokemon, enemyPokemon):
    teamScore = 0


    for poke_id, pokemon in ourPokemon.items():  
        #sum over all possible status effects, 
        status_effect = (1 - 0.5*sum(pokemon.status.values())) 
        stat_multiplier = 1 
        stat_multiplier *= (2+ pokemon.atk_stage[0])/(2 - pokemon.atk_stage[1])
        stat_multiplier *= (2+ pokemon.def_stage[0])/(2 - pokemon.def_stage[1])
        stat_multiplier *= (2+ pokemon.spa_stage[0])/(2 - pokemon.spa_stage[1])
        #stat_multiplier *= (2+ pokemon.spd_stage[0])/(2 - pokemon.spd_stage[1]) gen1
        stat_multiplier *= (2+ pokemon.spe_stage[0])/(2 - pokemon.spe_stage[1])
      #for stat,mult in pokemon.stat_multipliers.items():
        #if pokemon.gen == 1 and stat == 3:
        #    continue
        #stat_multiplier *= stat
        teamScore += pokemon.currhp*status_effect*stat_multiplier
    teamScore = teamScore / NUM_TEAM_MEMBERS
    #if enemyPokemon.status != "None":
    #  status_effect = 0.5
    #else:
    #  status_effect = 1
    #stat_multiplier = 1

    #for stat, mult in enemyPokemon.stat_multipliers.items():
    #    if enemyPokemon.gen == 1 and stat == 3:
    #        continue
    #    stat_multiplier *= mult
    pokemon = enemyPokemon
    status_effect = (1 - 0.5*sum(pokemon.status.values()))
    stat_multiplier = 1 
    stat_multiplier *= (2+ pokemon.atk_stage[0])/(2 - pokemon.atk_stage[1])
    stat_multiplier *= (2+ pokemon.def_stage[0])/(2 - pokemon.def_stage[1])
    stat_multiplier *= (2+ pokemon.spa_stage[0])/(2 - pokemon.spa_stage[1])
    #stat_multiplier *= (2+ pokemon.spd_stage[0])/(2 - pokemon.spd_stage[1]) gen1
    stat_multiplier *= (2+ pokemon.spe_stage[0])/(2 - pokemon.spe_stage[1])
    enemyScore = enemyPokemon.currhp*status_effect*stat_multiplier
    score = teamScore - enemyScore
    return score

def isWin(enemyPokemon):
    return enemyPokemon.currhp <= 0 

def isLose(ourPokemon):
    allFainted = True 
    for pokemon in ourPokemon.values():
        if pokemon.currhp > 0:
            allFainted = False
    return allFainted



def main():
    # (attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types)
    poke1 = Pokemon("1", 90, 90, 100, 1, 100, 353, 100, 1.0,
                    1, ['blizzard'], ['fire', 'water'], None, {0:1, 1:1, 2:1, 3:1, 4:1})
    poke2 = Pokemon("2", 90, 90, 100, 2, 100, 353, 100, 1.0,
                    1, ['blizzard'], ['fire', 'water'], None, {0:1, 1:1, 2:1, 3:1, 4:1})

    nextStates = performActions(poke1, poke2, ("move", "blizzard"), ("move", "agility"))
    nextStates = performActions(nextStates[0][1][0], nextStates[0][1][1], ("move", "blizzard"), ("move", "agility"))
    nextStates = performActions(nextStates[0][1][0], nextStates[0][1][1], ("move", "blizzard"), ("move", "fireblast"))
    nextStates = performActions(nextStates[0][1][0], nextStates[0][1][1], ("move", "blizzard"), ("move", "bubblebeam"))


#nextStates = performActions(
    #    nextStates[0][1][0], nextStates[0][1][1], ("move", "blizzard"), ("move", "blizzard"))
    print(json.dumps(json.loads(jsonpickle.encode(nextStates)), indent=2))


if __name__ == "__main__":
    main()
