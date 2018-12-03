var SYNC_REQUEST = require('sync-request');
const GEN = "gen1"
const MODS_DIR = '../../../../../mods/'
const DATA_DIR = '../../../../../data/'
const FORMATS_DATA = require(MODS_DIR + GEN + "/formats-data").BattleFormatsData
const MOVES = require(DATA_DIR + "moves").BattleMovedex
const POKEDEX = require(DATA_DIR + "pokedex").BattlePokedex
const TYPES = require(DATA_DIR + 'typechart').BattleTypeChart
const SPECIAL_CHARS = /[%\s\.'-]/g

var ourBaseStats = {}
var theirBaseStats = {}
var turn = 0

var getBestMove = exports.getBestMove = (battle, decisions) => {
    let foePokemon = battle.request.side.pokemon.filter(pokemon => pokemon.active)[0]
    let foeName = formatName(battle.foe.pokemon[0].species)

    // Get valid moves sorted by maxpp
    let moves = battle.request.active[0].moves.map((move, i) => {
        move['index'] = i + 1
        return move
    }).filter(
        move => !move.disabled
    ).sort(function(a, b) {
        return a.maxpp - b.maxpp
    })

    // Get random of strongest 2 moves
    let move = moves[moves.length > 1? Math.round(Math.random()): 0]
    let decision = decisions.filter(decision => move.move == decision[0].move)[0]

    try {
        var damageArray = {}
        var theirMoves = []

        // Damage calculated for each move
        let damageCalculator = calculateDamage(battle, moves)
        console.log(damageCalculator)
        for (let i = 0; i < damageCalculator.length; i++) {
            damageArray[damageCalculator[i][1]['id']] = damageCalculator[i][0]
        }

        if (FORMATS_DATA.hasOwnProperty(foeName)) {
            if (FORMATS_DATA[foeName].hasOwnProperty('randomBattleMoves')) {
                theirMoves = theirMoves.concat(FORMATS_DATA[foeName]["randomBattleMoves"])
                // console.log("THEIR MOVES 1:", theirMoves)
            } else {
                console.log("FORMATS_DATA[foeName]", FORMATS_DATA[foeName])
            }
        } else { 
            console.log("ISSUE WITH FORMATS_DATA")
        }

        if (FORMATS_DATA[foeName].hasOwnProperty('essentialMove')) {
            theirMoves = theirMoves.concat(FORMATS_DATA[foeName]['essentialMove'])
        }
        if (FORMATS_DATA[foeName].hasOwnProperty('exclusiveMoves')) {
            // console.log("THEIR MOVES 2:", theirMoves)
            theirMoves = theirMoves.concat(FORMATS_DATA[foeName]["exclusiveMoves"])
        }

        let ourCondition = {}
        let ourStats = {}
        let ourMoves = {}
        let ourDetails = {}
        let ourTypes = {}
        let ourPokemon = {}
        var ourPokemonIndices = {}

        console.log("MADE IT THIS FAR")
        for (pokemon of battle.request.side.pokemon) {
            let pokedexNum = POKEDEX[getPokemonName(pokemon)].num
            ourCondition[pokedexNum] = pokemon.condition
            ourStats[pokedexNum] = pokemon.stats
            ourMoves[pokedexNum] = pokemon.moves
            ourDetails[pokedexNum] = pokemon.details
            ourTypes[pokedexNum] = POKEDEX[getPokemonName(pokemon)].types
            ourPokemon[pokedexNum] = pokedexNum

            if (pokedexNum == POKEDEX[getPokemonName(pokemon)].num) {
                let moveList = []
                //console.log("moves are ", moves)
                for (let j = 0; j < moves.length; j++) {
                    //console.log("move state is ", moves[j].disabled)
                    if (moves[j].disabled == false) {
                        moveList.push(moves[j].id)
                    } 
                }
                ourMoves[pokedexNum] = moveList
            }
        }

        if (!theirBaseStats.hasOwnProperty(POKEDEX[foeName].num)) {
            theirBaseStats[POKEDEX[foeName].num] = foePokemon['stats']
        }

        if (turn == 1) {
            //console.log("base stats set!")
            ourBaseStats = JSON.parse(JSON.stringify(ourStats));
        } //implement proper basestat module 

        if (moves.length == 1) { //handles recharge moves 
            return ("move " + moves[0].id)
        }

        console.log(foePokemon, theirMoves)
        if (!POKEDEX.hasOwnProperty(foeName)) {
            console.log("ISSUES ON THE HORIZON")
        }
        var ret = SYNC_REQUEST('POST', 'http://127.0.0.1:5000/getaction', {
            json: {
                generation: GEN,
                currPokemon: POKEDEX[foeName].num,
                ourPokemon: ourPokemon,
                theirPokemon: POKEDEX[foeName].num,
                ourHp: ourCondition,
                theirHp: foePokemon['condition'],
                ourMoves: ourMoves,
                theirMoves: theirMoves,
                ourStats: ourStats,
                theirStats : foePokemon['stats'],
                ourDetails: ourDetails,
                theirDetails: foePokemon['details'],
                ourTypes: ourTypes,
                theirTypes: POKEDEX[foeName].types,
                theirTypes: POKEDEX[foeName].types,
                ourBaseStats: ourBaseStats,
                theirBaseStats: theirBaseStats
            }
        });
        console.log("SYNC_REQUEST COMPLETE")
        var action = ret.body.toString('utf8');
        if (action.startsWith("switch")) {
            pokedexNum = action.split(" ")[1];
            action = "switch " + ourPokemonIndices[pokedexNum];
        }
    } catch (error) {
        console.log(error)
    }

    // If no viable moves, choose any move
    if (decision.length == 0) {
        let viableMoves = decisions.filter(decision => decision[0].type == 'move')
        return viableMoves[viableMoves.length > 0 ? Math.floor(Math.random() * viableMoves.length-1): 0]
    }

    return decision
}

var getBestSwitch = exports.getBestSwitch = (battle, decisions) => {
    let foePokemon = battle.foe.pokemon[0].species
    let foeName = formatName(foePokemon)
    // fainted++
    
    // Get available pokemon sorted by level
    let availablePokemon = battle.request.side.pokemon.map((pokemon, i) => {
        pokemon['index'] = i + 1
        return pokemon
    }).filter(pokemon => (
        // not active
        !pokemon.active &&
        // not fainted
        !pokemon.condition.endsWith(` fnt`)
    )).sort(function(a, b) {
        let high = Number(b.details.split(", ")[1].substring(1))
        let low = Number(a.details.split(", ")[1].substring(1))
        return low - high
    })

    // Get types sorted by damage to foe
    let damageTaken = []
    for (let entry of POKEDEX[foeName]['types']) {
        for (let pokeType in TYPES[entry]['damageTaken']) {
            if (TYPES[entry]['damageTaken'][pokeType] != 0) {
                damageTaken.push([pokeType, TYPES[entry]['damageTaken'][pokeType]])
            }
        }
    }
    damageTaken.sort(function(a, b) { return b[1] - a[1] })

    // Return pokemon which inflicts most damage based on type
    for (let pokeType of damageTaken) {
        for (let bestPokemon of availablePokemon) {
            if (POKEDEX[getPokemonName(bestPokemon)].types.includes(pokeType[0])) {
                let decision = decisions.filter(decision => decision[0].poke == bestPokemon.ident)
                if (decision.length > 0){
                    return decision[0]
                }
            }
        }
    }

    // Return random pokemon
    let switchDecisions = decisions.filter(decision => decision.type == 'switch')
    return decisions[Math.floor(Math.random() * decisions.length-1)]
}

/*
 * Helper Functions
 */
var calculateDamage = (battle, moves) => {
    // Apply Battle Damage Formula:
    // ((2A/5+2)*B*C)/D)/50)+2)*X)*Y/10)*Z)/255
    // 
    // A = attacker's Level
    // B = attacker's Attack or Special
    // C = attack Power
    // D = defender's Defense or Special
    // X = same-Type attack bonus (1 or 1.5)
    // Y = Type modifiers (40, 20, 10, 5, 2.5, or 0)
    // Z = a random number between 217 and 255

    // Get available pokemon sorted by level
    let attacker = formatName(battle.self.pokemon[0].species)
    let defender = formatName(battle.foe.pokemon[0].species)
    console.log("ATTACKER: ", attacker)
    console.log("DEFENDER: ", defender)
 
    let moveDamage = []
    for (let move of moves) {
        let moveName = formatName(move.move)
        console.log(moveName)
        // Handle edge case causing crashes
        if (moveName == 'return102') {
            moveName = 'return'
        }
        var damage = 0
        let level = Number(battle.self.pokemon[0].level)
        console.log("getting attack stat")
        let attack = getAttackStat(attacker, moveName)
        console.log("getting basepower")
        let basePower = Number(MOVES[moveName].basePower)
        console.log("getting defense stat")
        let defense = getDefenseStat(defender, moveName)
        console.log("getting type multiplier")
        let sameType = sameTypeMultiplier(attacker, moveName)
        console.log("getting attack type multiplier")
        let attackType = attackTypeMultiplier(defender, moveName)
        let randomNum = getRandomInt(217, 255+1)
        if (move.hasOwnProperty("status")) {
            damage = -1
        } else {
            damage = ((((2 * level / 5 + 2) * attack / defense) / 50) + 2) * (sameType * attackType * randomNum)
        }
        moveDamage.push([damage, move])
    }

    console.log("calculateDamage SUCCESS")
    return moveDamage 
}

var formatName = (name) => {
    return name.toLowerCase().replace(SPECIAL_CHARS, "")
}

var getAttackStat = (attacker, move) => {
    let attack = 0
    if (!(move in MOVES)) console.log("ATTACK MOVE " + move + " NOT IN MOVES")
    if (MOVES[move].category == "Special") {
        attack = POKEDEX[attacker].baseStats.spa
    } else if (MOVES[move].category == "Physical") {
        attack = POKEDEX[attacker].baseStats.atk
    } else {
        // console.log("!!! HANDLE THIS CASE !!! : ", move, MOVES[move])
        attack = POKEDEX[attacker].baseStats.atk
    }
    
    return Number(attack)
}

function getDefenseStat(defender, move) {
    let defense = 0
 
    if (MOVES[move].category == "Special") {
        defense = POKEDEX[defender].baseStats.spd
    } else if (MOVES[move].category == "Physical") {
        defense = POKEDEX[defender].baseStats.def
    } else {
        // console.log("!!! HANDLE THIS CASE !!! : ", move, MOVES[move])
        defense = POKEDEX[defender].baseStats.def
    }
 
    return Number(defense)
}

var sameTypeMultiplier = (attacker, move) => {
    if (POKEDEX[attacker].types.includes(MOVES[move].type)) {
        return 1.5
    }
    return 1
}

var attackTypeMultiplier = (defender, move) => {
    let damageTaken = 1
    for (let pokeType of POKEDEX[defender].types) {
        damageTaken *= Number(TYPES[pokeType].damageTaken[MOVES[move].type])
    }
    return Number(damageTaken)
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return min + Math.floor(Math.random() * (max - min + 1));
}

var getPokemonName = (pokemon) => {
    return pokemon.details.split(", ")[0].toLowerCase().replace(SPECIAL_CHARS, "")
}
