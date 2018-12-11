import copy
import csv
import json
import math
from statistics import mean

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
    _maxhp = None
    level = None
    currhp = 1.0
    gen = None
    moveids = []
    types = []
    stat_multipliers = None
    last_dmg_taken = 0
    last_move_taken = None
    last_move_used = None

    recharge = False

    status = {"brn": 0, "frz": 0, "par": 0, "psn": 0, "slp": 0, "tox": 0}

    # From random team generator. EVs are exact, IVs are expected values
    evs = {"hp": 255, "atk": 255, "def": 255, "spa": 255, "spd": 255, "spe": 255}
    ivs = {"hp": 16, "atk": 16, "def": 16, "spa": 16, "spd": 16, "spe": 16}

    atk_stage = 0
    def_stage = 0
    spa_stage = 0
    spd_stage = 0
    spe_stage = 0

    #_tox_stage = 1

    def __init__(self, poke_id, attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types, status, stat_multipliers):
        self.poke_id = str(poke_id)
        self._attack = attack
        self._defense = defense
        self._sp_att = sp_att
        self._sp_def = sp_def
        self._speed = speed
        self._maxhp = maxhp
        self.level = level
        self.currhp = currhp
        self.gen = gen
        self.moveids = moveids
        self.types = types
        self.stat_multipliers = stat_multipliers
        if status != "None":
            self.status = {"brn": 0, "frz": 0, "par": 0, "psn": 0, "slp": 0, "tox": 0}
            self.status[status] = 1.0
        else:
            self.status = {"brn": 0, "frz": 0, "par": 0, "psn": 0, "slp": 0, "tox": 0}
        self.atk_stage = stat_multipliers.get('atk', 0)
        self.def_stage = stat_multipliers.get('def', 0)
        self.spa_stage = stat_multipliers.get('spa', 0)
        self.spd_stage = stat_multipliers.get('spd', 0)
        self.spe_stage = stat_multipliers.get('spe', 0)
        #self._tox_stage = _tox_stage

    def stage_to_multiplier(self, stage):
        return max(2, 2 + stage) / max(2, 2 - stage)

    def damage(self, damage):
        self.last_dmg_taken = damage
        self.currhp -= damage / self.maxhp

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
        stat = int(((self._attack + self.ivs['atk']) * 2 + math.sqrt(self.evs['atk'] / 4)) * self.level / 100 + 5)
        return int(stat * self.stage_to_multiplier(self.atk_stage) * (1 - 0.5 * self.status['brn']))

    @property
    def defense(self):
        stat = int(((self._defense + self.ivs['def']) * 2 + math.sqrt(self.evs['def'] / 4)) * self.level / 100 + 5)
        return int(stat * self.stage_to_multiplier(self.def_stage))

    @property
    def sp_att(self):
        stat = int(((self._sp_att + self.ivs['spa']) * 2 + math.sqrt(self.evs['spa'] / 4)) * self.level / 100 + 5)
        return int(stat * self.stage_to_multiplier(self.spa_stage))

    @property
    def sp_def(self):
        stat = int(((self._sp_def + self.ivs['spd']) * 2 + math.sqrt(self.evs['spd'] / 4)) * self.level / 100 + 5)
        return int(stat * self.stage_to_multiplier(self.spd_stage))

    @property
    def speed(self):
        stat = int(((self._speed + self.ivs['spe']) * 2 + math.sqrt(self.evs['spe'] / 4)) * self.level / 100 + 5)
        return int(stat * self.stage_to_multiplier(self.spe_stage) * (1 - 0.25 * self.status['par']))

    @property
    def maxhp(self):
        return int(((self._maxhp + self.ivs['hp']) * 2 + math.sqrt(self.evs['hp']) / 4) * self.level / 100 + self.level + 10)

    def __str__(self):
        currhpint = round(self.currhp * self.maxhp)
        return "Pokemon {}: {{Status: {}/{} ({}), Level: {}, Types: {}, Base Stats: ({}, {}, {}, {}, {}), Effective Stats: ({}, {}, {}, {}, {}), Moves: {}}}".format(
            self.poke_id,
            currhpint,
            self.maxhp,
            self.status,
            self.level,
            self.types,
            self._attack,
            self._defense,
            self._sp_att,
            self._sp_def,
            self._speed,
            self.attack,
            self.defense,
            self.sp_att,
            self.sp_def,
            self.speed,
            self.moveids
        )

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result.status = self.status.copy()
        return result

def calcEffectiveness(move, defendingPokemon):
    effectivenesses = [move_effectiveness[(
        move.type, def_type.lower())] for def_type in defendingPokemon.types]
    effectiveness = 1
    for e in effectivenesses:
        effectiveness = effectiveness * e
    return effectiveness

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
        effectiveness = calcEffectiveness(move, defendingPokemon)
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

def prob_fainted(hp):
    a = 1
    b = 10
    c = 0
    return 1 / (1 + a * math.exp(b * hp) + c)

def calc_acc_factor(move, pokemon):
    if move.accuracy is True:
        acc = 1.0
    else:
        acc = move.accuracy / 100.0

    # Add a prob_fainted parameter so that move order actually matters. This parameter influences accuracy based on
    # probability that the attacking pokemon is fainted, accounting for advantages in going first
    prob_alive = 1 - prob_fainted(pokemon.currhp)
    acc *= prob_alive
    # Handle paralysis
    acc *= 1 - pokemon.status['par'] * 0.25
    acc *= 1 - pokemon.status['slp']
    return acc

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
        self.damage = movedata.get('damage', None)
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
        ourPokemon_new.last_move_used = self
        theirPokemon_new.last_move_taken = self
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
        acc = calc_acc_factor(self, ourPokemon_new)

        if isinstance(self.multihit, list):
            multihit = mean(self.multihit)
        else:
            multihit = self.multihit

        # Do damage calc first
        if self.basePower != 0:
            if self.damage is not None:
                damage = self.damage
            else:
                damage = calcDamage(ourPokemon_new, theirPokemon_new, self)
            theirPokemon_new.damage(damage * acc * multihit)


        # Then apply boosts if they exist
        if self.boosts is not None:
            # Apply boost to self
            if self.accuracy is True:
                ourPokemon_new.atk_stage = min(6, self.boosts.get("atk", 0) + ourPokemon_new.atk_stage)
                ourPokemon_new.def_stage = min(6, self.boosts.get("def", 0) + ourPokemon_new.def_stage)
                ourPokemon_new.spa_stage = min(6, self.boosts.get("spa", 0) + ourPokemon_new.spa_stage)
                ourPokemon_new.spe_stage = min(6, self.boosts.get("spe", 0) + ourPokemon_new.spe_stage)
            # Otherwise, apply boosts to opponent
            else:
                theirPokemon_new.atk_stage = max(-6, self.boosts.get("atk", 0) * acc + theirPokemon_new.atk_stage)
                theirPokemon_new.def_stage = max(-6, self.boosts.get("def", 0) * acc + theirPokemon_new.def_stage)
                theirPokemon_new.spa_stage = max(-6, self.boosts.get("spa", 0) * acc + theirPokemon_new.spa_stage)
                theirPokemon_new.spe_stage = max(-6, self.boosts.get("spe", 0) * acc + theirPokemon_new.spe_stage)

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
                theirPokemon_new.atk_stage = max(-6, self.secondary['boosts'].get("atk", 0) * secondary_acc + theirPokemon_new.atk_stage)
                theirPokemon_new.def_stage = max(-6, self.secondary['boosts'].get("def", 0) * secondary_acc + theirPokemon_new.def_stage)
                theirPokemon_new.spa_stage = max(-6, self.secondary['boosts'].get("spa", 0) * secondary_acc + theirPokemon_new.spa_stage)
                theirPokemon_new.spe_stage = max(-6, self.secondary['boosts'].get("spe", 0) * secondary_acc + theirPokemon_new.spe_stage)

        return [(1.0, (ourPokemon_new, theirPokemon_new))]

    def bide(self, ourPokemon, theirPokemon):
        #print("bide")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]

    def counter(self, ourPokemon, theirPokemon):
        theirPokemon_new = copy.copy(theirPokemon)
        if ourPokemon.last_move_taken is not None and ourPokemon.last_move_taken.basePower != 0 and ourPokemon.last_move_taken.type in ['normal', 'fighting']:
            theirPokemon_new.damage(ourPokemon.last_dmg_taken * 2)
        return [(1.0, (copy.copy(ourPokemon), theirPokemon_new))]

    def explosion(self, ourPokemon, theirPokemon):
        ourPokemon_new = copy.copy(ourPokemon)
        theirPokemon_new = copy.copy(theirPokemon)
        acc = calc_acc_factor(self, ourPokemon_new)
        their_poke_orig_def = theirPokemon_new._defense
        theirPokemon_new._defense = theirPokemon_new._defense * 0.5
        damage = calcDamage(ourPokemon_new, theirPokemon_new, self)
        theirPokemon_new.damage(damage * acc)
        theirPokemon_new._defense = their_poke_orig_def
        ourPokemon_new.currhp = -1 # do -1 and not 0, because 0 doesn't mean fully fainted in our model
        return [(1.0, (ourPokemon_new, theirPokemon_new))]

    selfdestruct = explosion

    def megadrain(self, ourPokemon, theirPokemon):
        result = self.defaultmove(ourPokemon, theirPokemon)
        acc = calc_acc_factor(self, ourPokemon)
        result[0][1][0].currhp += result[0][1][1].last_dmg_taken * acc * 1/2 / result[0][1][0].maxhp
        return result

    def mirrormove(self, ourPokemon, theirPokemon):
        if theirPokemon.last_move_used is not None:
            result = theirPokemon.last_move_used.effect(ourPokemon, theirPokemon)
        else:
            result = [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]
        return result

    def doubleedge(self, ourPokemon, theirPokemon):
        result = self.defaultmove(ourPokemon, theirPokemon)
        result[0][1][0].damage(result[0][1][1].last_dmg_taken / 4)
        return result

    submission = doubleedge

    def superfang(self, ourPokemon, theirPokemon):
        ourPokemon_new = copy.copy(ourPokemon)
        theirPokemon_new = copy.copy(theirPokemon)
        acc = calc_acc_factor(self, ourPokemon_new)
        theirPokemon_new.damage(theirPokemon_new.currhp * acc * theirPokemon_new.maxhp * 0.5)
        return [(1.0, (ourPokemon_new, theirPokemon_new))]

    def psywave(self, ourPokemon, theirPokemon):
        ourPokemon_new = copy.copy(ourPokemon)
        theirPokemon_new = copy.copy(theirPokemon)
        acc = calc_acc_factor(self, ourPokemon_new)
        effectiveness = calcEffectiveness(self, theirPokemon_new)
        damage = effectiveness * ourPokemon_new.level * acc
        theirPokemon_new.damage(damage)
        return [(1.0, (ourPokemon_new, theirPokemon_new))]

    def seismictoss(self, ourPokemon, theirPokemon):
        ourPokemon_new = copy.copy(ourPokemon)
        theirPokemon_new = copy.copy(theirPokemon)
        acc = calc_acc_factor(self, ourPokemon_new)
        damage = ourPokemon_new.level * acc
        theirPokemon_new.damage(damage)
        return [(1.0, (ourPokemon_new, theirPokemon_new))]

    nightshade = seismictoss

    def recover(self, ourPokemon, theirPokemon):
        ourPokemon_new = copy.copy(ourPokemon)
        theirPokemon_new = copy.copy(theirPokemon)
        acc = calc_acc_factor(self, ourPokemon_new)
        ourPokemon_new.currhp = min(ourPokemon_new.currhp + acc * 0.5, 1)
        return [(1.0, (ourPokemon_new, theirPokemon_new))]

    softboiled = recover

    def rest(self, ourPokemon, theirPokemon):
        ourPokemon_new = copy.copy(ourPokemon)
        theirPokemon_new = copy.copy(theirPokemon)
        ourPokemon_new.status = {"brn":0, "frz":0, "par":0, "psn":0, "slp":1, "tox":0}
        ourPokemon_new.currhp = 1.0
        return [(1.0, (ourPokemon_new, theirPokemon_new))]

    def transform(self, ourPokemon, theirPokemon):
        ourPokemon_new = copy.copy(theirPokemon)
        theirPokemon_new = copy.copy(theirPokemon)
        return [(1.0, (ourPokemon_new, theirPokemon_new))]

    def reflect(self, ourPokemon, theirPokemon):
        #print("reflect")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]

    def substitute(self, ourPokemon, theirPokemon):
        #print("substitute")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]

    def hyperbeam(self, ourPokemon, theirPokemon):
        ourPokemon.recharge = True
        return self.defaultmove(ourPokemon, theirPokemon)


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
    if team_poke[curr_poke].recharge:
        team_poke[curr_poke].recharge = False
        return [("switch", team_poke[curr_poke])]
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

def getHpScore(hp):
    '''
    Scoring function for HP, to allow non-linear scores for HP (presumably, doing damage at high HP isn't super important, but you wanna KO at lower HP
    :param hp:
    :return:
    '''
    a = 1
    b = 5
    c = 0
    return -1 / (1 + a * math.exp(b * hp) + c) + 1

def getScore(ourPokemon, enemyPokemon):
    teamScore = 0


    for poke_id, pokemon in ourPokemon.items():
        #sum over all possible status effects, 
        status_effect = (1 - 0.5*sum(pokemon.status.values()))
        #status_effect = 1
        stat_multiplier = 1
        stat_multiplier *= pokemon.stage_to_multiplier(pokemon.atk_stage)
        stat_multiplier *= pokemon.stage_to_multiplier(pokemon.def_stage)
        stat_multiplier *= pokemon.stage_to_multiplier(pokemon.spa_stage)
        #stat_multiplier *= pokemon.stage_to_multiplier(pokemon.spd_stage)
        stat_multiplier *= pokemon.stage_to_multiplier(pokemon.spe_stage)
        #for stat,mult in pokemon.stat_multipliers.items():
        #if pokemon.gen == 1 and stat == 3:
        #    continue
        #stat_multiplier *= stat
        teamScore += getHpScore(pokemon.currhp)*status_effect*(stat_multiplier ** 0.5)
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
    #status_effect = 1
    stat_multiplier = 1
    stat_multiplier *= pokemon.stage_to_multiplier(enemyPokemon.atk_stage)
    stat_multiplier *= pokemon.stage_to_multiplier(enemyPokemon.def_stage)
    stat_multiplier *= pokemon.stage_to_multiplier(enemyPokemon.spa_stage)
    #stat_multiplier *= pokemon.stage_to_multiplier(enemyPokemon.spd_stage)
    stat_multiplier *= pokemon.stage_to_multiplier(enemyPokemon.spe_stage)
    enemyScore = getHpScore(enemyPokemon.currhp)*status_effect*(stat_multiplier ** 0.5)
    score = teamScore - enemyScore * 1.5 # Favor doing damage to opponent rather than helping self
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

    nextStates = performActions(poke1, poke2, ("move", "blizzard"), ("move", "counter"))

    testpoke1 = Pokemon(1, 136, 115, 197, 197, 197, 229, 68, 0.677, 1, ['blizzard', 'lovelykiss', 'psychic', 'seismictoss'],['ice', 'psychic'], None, {0:1, 1:1, 2:1, 3:1, 4:1})
    testpoke2 = Pokemon(1, 136, 129, 251, 251, 173, 216, 68, 0.29, 1, ['psychic', 'thunderwave', 'recover', 'reflect', 'reflect', 'counter', 'seismictoss', 'seismictoss'], ['psychic'], "par", {0:1, 1:1, 2:1, 3:1, 4:1})

    nextStates = performActions(testpoke1, testpoke2, ("move", "lovelykiss"), ("move", "thunderwave"))


    #nextStates = performActions(
    #    nextStates[0][1][0], nextStates[0][1][1], ("move", "blizzard"), ("move", "blizzard"))
    print(json.dumps(json.loads(jsonpickle.encode(nextStates)), indent=2))


if __name__ == "__main__":
    main()