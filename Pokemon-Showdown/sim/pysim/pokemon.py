import copy
import csv
import json
import jsonpickle

move_effectiveness = {}
viable_moves = {}


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

    status = None
    atk_stage = 0
    def_stage = 0
    spa_stage = 0
    spd_stage = 0
    spe_stage = 0

    _tox_stage = 1

    def __init__(self, attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types):
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

    def stage_to_multiplier(self, stage):
        return max(2, 2 + stage) / max(2, 2 - stage)

    def handle_status(self):
        '''
        Handles status effects in place. Run on the Pokemon instance after performing actions.
        :return:
        '''
        if self.status == "brn":
            self.currhp -= 1.0/16.0
        elif self.status == "frz":
            pass
        elif self.status == "par":
            pass
        elif self.status == "psn":
            self.currhp -= 1.0/16.0
        elif self.status == "slp":
            pass
        elif self.status == "tox":
            self.currhp -= self._tox_stage/16.0
            self._tox_stage += 1

    @property
    def attack(self):
        return int(self._attack * self.stage_to_multiplier(self.atk_stage) * (0.5 if self.status == "brn" else 1))

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
        return int(self._speed * self.stage_to_multiplier(self.spe_stage) * (0.25 if self.status == "par" else 1))


def calcDamage(attackingPokemon, defendingPokemon, move):
    if attackingPokemon.gen == 1:
        critchance = attackingPokemon.speed / 512 * 8 ** (move.critratio - 1)
        level = attackingPokemon.level * (1 * (
            1 - critchance) + 2 * critchance)  # Expected value for level, taking into account crit chance

        effectivenesses = [move_effectiveness[(
            move.type, def_type)] for def_type in defendingPokemon.types]
        effectiveness = 1
        for e in effectivenesses:
            effectiveness = effectiveness * e
        stab = 1.5 if move.type in attackingPokemon.types else 1
        modifier = stab * effectiveness

        if move.category.lower() == "physical":
            a = attackingPokemon.attack
            d = defendingPokemon.defense
        else:
            a = attackingPokemon.sp_att
            d = defendingPokemon.sp_att

        basedmg = int(int(int(2 * level / 5 + 2) *
                          move.basePower * a / d) / 50 + 2)
        random = list(range(217, 256))  # all random values
        damage_values = [int(basedmg * modifier * r / 255.0) for r in random]
        return sum(damage_values) / len(damage_values)
    else:
        raise (NotImplementedError(
            "Generation {} not implemented yet".format(attackingPokemon.gen)))


def performActions(p1_pokemon, p2_pokemon, p1action, p2action):
    ret = []

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
        ourPokemon_hit = copy.copy(ourPokemon)
        theirPokemon_hit = copy.copy(theirPokemon)

        states = []
        # First, check for freeze/sleep and do nothing if we're frozen/sleeped
        if ourPokemon_hit.status == "frz" or ourPokemon_hit.status == "slp":
            return [(1.0, (ourPokemon_hit, theirPokemon_hit))]
        # Add missed state first, if accuracy is <100
        if self.accuracy is True:
            acc = 1.0
        else:
            acc = self.accuracy / 100.0

        # Handle paralysis
        if ourPokemon_hit.status == "par":
            acc *= 0.25

        if acc != 1.0:
            states.append(
                (1.0 - acc, (copy.copy(ourPokemon), copy.copy(theirPokemon))))

        # Do damage calc first
        if self.basePower != 0:
            damage = calcDamage(ourPokemon_hit, theirPokemon_hit, self)
            theirPokemon_hit.currhp -= damage / theirPokemon_hit.maxhp

        # Then apply boosts if they exist
        if self.boosts is not None:
            # Apply boost to self
            if self.accuracy is True:
                ourPokemon_hit.atk_stage += self.boosts.get("atk", 0)
                ourPokemon_hit.def_stage += self.boosts.get("def", 0)
                ourPokemon_hit.spa_stage += self.boosts.get("spa", 0)
                #ourPokemon_hit.sp_def += self.boosts.get("spd",0)
                ourPokemon_hit.spe_stage += self.boosts.get("spe", 0)
            # Otherwise, apply boosts to opponent
            else:
                theirPokemon_hit.atk_stage += self.boosts.get("atk", 0)
                theirPokemon_hit.def_stage += self.boosts.get("def", 0)
                theirPokemon_hit.spa_stage += self.boosts.get("spa", 0)
                #theirPokemon_hit.sp_def += self.boosts.get("spd",0)
                theirPokemon_hit.spe_stage += self.boosts.get("spe", 0)

        # Apply status effect if there is one
        if self.status is not None and theirPokemon_hit.status is None:
            # Except fire-type moves can't burn fire-type pokemon
            if not (self.status == "brn" and self.type == "fire" and "fire" in theirPokemon.types):
                theirPokemon_hit.status = self.status
                theirPokemon_hit._tox_stage = 1

        # If their Pokemon is frozen and this is a physical fire-type move that can burn, unfreeze them
        if theirPokemon_hit.status == "frz" and self.type == "fire" and self.status == "brn" and self.category == "physical":
            theirPokemon_hit.status = None

        # Then, apply secondary effects if they exist
        if self.secondary is not None:
            secondary_acc = self.secondary['chance'] / 100.0
            ourPokemon_secondary = copy.copy(ourPokemon_hit)
            theirPokemon_secondary = copy.copy(theirPokemon_hit)
            if "status" in self.secondary.keys() and theirPokemon_secondary.status is None:
                theirPokemon_secondary.status = self.secondary['status']
            if "boosts" in self.secondary.keys():
                theirPokemon_secondary.atk_stage += self.secondary['boosts'].get(
                    "atk", 0)
                theirPokemon_secondary.def_stage += self.secondary['boosts'].get(
                    "def", 0)
                theirPokemon_secondary.spa_stage += self.secondary['boosts'].get(
                    "spa", 0)
                #theirPokemon_secondary.sp_def += self.secondary['boosts'].get("spd",0)
                theirPokemon_secondary.spe_stage += self.secondary['boosts'].get(
                    "spe", 0)
            states.append(
                (acc * secondary_acc, (ourPokemon_secondary, theirPokemon_secondary)))
            states.append((acc * (1 - secondary_acc),
                           (ourPokemon_hit, theirPokemon_hit)))
        else:
            states.append((acc, (ourPokemon_hit, theirPokemon_hit)))
        return states

    def bide(self, ourPokemon, theirPokemon):
        print("bide")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]

    def counter(self, ourPokemon, theirPokemon):
        print("counter")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]

    def reflect(self, ourPokemon, theirPokemon):
        print("reflect")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]

    def substitute(self, ourPokemon, theirPokemon):
        print("substitute")
        return [(1.0, (copy.copy(ourPokemon), copy.copy(theirPokemon)))]


with open('viablemovesdata.json') as f:
    move_data = json.loads(f.read())
    for id, data in move_data.items():
        viable_moves[id] = Move(data)

with open('effectiveness.csv', 'rt') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        move_effectiveness[(row[0], row[1])] = float(row[2])


def main():
    # (attack, defense, sp_att, sp_def, speed, maxhp, level, currhp, gen, moveids, types)
    poke1 = Pokemon(90, 90, 100, 1, 100, 353, 100, 1.0,
                    1, ['blizzard'], ['fire', 'water'])
    poke1_2 = Pokemon(90, 90, 100, 3, 100, 353, 100, 1.0,
                      1, ['blizzard'], ['grass', 'ground'])
    poke2 = Pokemon(90, 90, 100, 2, 100, 353, 100, 1.0,
                    1, ['blizzard'], ['fire', 'water'])



    nextStates = performActions(
        poke1, poke2, ("move", "spore"), ("move", "agility"))
    nextStates = performActions(
        nextStates[0][1][0], nextStates[0][1][1], ("move", "blizzard"), ("move", "blizzard"))
    print(json.dumps(json.loads(jsonpickle.encode(nextStates)), indent=2))


if __name__ == "__main__":
    main()
