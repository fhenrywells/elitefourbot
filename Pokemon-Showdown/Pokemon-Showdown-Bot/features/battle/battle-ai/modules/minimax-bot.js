'use strict';
var SYNC_REQUEST = require('sync-request');

const GEN = "gen1"
const MODS_DIR = '../../../../../mods/'
const DATA_DIR = '../../../../../data/'
const FORMATS_DATA = require(MODS_DIR + GEN + "/formats-data").BattleFormatsData
const MOVES = require(DATA_DIR + "moves").BattleMovedex
const POKEDEX = require(MODS_DIR + GEN + "/pokedex").BattlePokedex
const TYPES = require(DATA_DIR + 'typechart').BattleTypeChart
const SPECIAL_CHARS = /[%\s\.'-]/g

// var turn = 1

var getBestMove = exports.getBestMove = (battle, decisions) => {
    let pokemonList = battle.request.side.pokemon
    let ourPokemon = battle.self.active[0]
    let ourName = formatName(ourPokemon.name)
    let foePokemon = battle.foe.active[0]
    let foeName = formatName(foePokemon.name)

    // Get valid moves sorted by maxpp
    let moves = battle.request.active[0].moves.map((move, i) => {
        move['index'] = i + 1
        return move
    }).filter(
        move => !move.disabled
    ).sort(function(a, b) {
        return a.maxpp - b.maxpp
    })

    //handles recharge moves 
    if (moves.length == 1) {
        console.log('DECISION', decisions.filter(decision => moves[0].move == decision[0].move)[0])
        return decisions.filter(decision => moves[0].move == decision[0].move)[0]
    }

    // Get random of strongest 2 moves
    let move = moves[moves.length > 1? Math.round(Math.random()): 0]
    let decision = decisions.filter(decision => move.move == decision[0].move)[0]

    try {
        // Damage calculated for each move
        // let damageCalculator = calculateDamage(battle, moves)
        // let damageArray = {}
        // for (let i = 0; i < damageCalculator.length; i++) {
        //     damageArray[damageCalculator[i][1]['id']] = damageCalculator[i][0]
        // }

        // Get all possible opponent moves
        let theirMoves = FORMATS_DATA[foeName]['randomBattleMoves']
        if (FORMATS_DATA[foeName].hasOwnProperty('essentialMove')) {
            theirMoves = theirMoves.concat(FORMATS_DATA[foeName]['essentialMove'])
        }
        if (FORMATS_DATA[foeName].hasOwnProperty('exclusiveMoves')) {
            theirMoves = theirMoves.concat(FORMATS_DATA[foeName]['exclusiveMoves'])
        }

        // Get our Pokemon's information
        let ourCondition = {}
        let ourStats = {}
        let ourMoves = {}
        let ourDetails = {}
        let ourTypes = {}
        let ourPokedexNumbers = {}
        let ourPokemonIndices = {}
        let ourBaseStats = {}

        for (let i = 0; i < pokemonList.length; i++) {
            let pokemonName = getPokemonName(pokemonList[i])
            let pokedexNum = POKEDEX[pokemonName].num

            ourCondition[pokedexNum] = pokemonList[i].condition
            ourStats[pokedexNum] = pokemonList[i].stats
            ourMoves[pokedexNum] = pokemonList[i].moves
            ourDetails[pokedexNum] = pokemonList[i].details
            ourTypes[pokedexNum] = POKEDEX[pokemonName].types
            ourPokedexNumbers[pokedexNum] = pokedexNum
            ourPokemonIndices[pokedexNum] = i + 1
            ourBaseStats[pokedexNum] = POKEDEX[pokemonName].baseStats

            if (pokedexNum == POKEDEX[pokemonName].num) {
                let moveList = []
                //console.log("moves are ", moves)
                for (let j = 0; j < moves.length; j++) {
                    if (moves[j].disabled == false) {
                        moveList.push(moves[j].id)
                    } 
                }
                ourMoves[pokedexNum] = moveList
            }
        }

        // Get move from minimaxserver.py
        var ret = SYNC_REQUEST('POST', 'http://127.0.0.1:5000/getaction', {
            json: {
                generation: GEN,
                currPokemon: POKEDEX[ourName].num,
                ourPokemon: ourPokedexNumbers,
                theirPokemon: POKEDEX[foeName].num,
                ourHp: ourCondition,
                theirHp: foePokemon.hp/100,
                theirStatus: foePokemon.status,
                ourMoves: ourMoves,
                theirMoves: theirMoves,
                ourStats: ourBaseStats,
                ourDetails: ourDetails,
                theirLevel: foePokemon.level,
                ourTypes: ourTypes,
                theirTypes: foePokemon.template.types,
                ourBaseStats: ourPokemon.template.baseStats,
                theirBaseStats: foePokemon.template.baseStats,
                ourBoosts: ourPokemon.boosts,
                theirBoosts: foePokemon.boosts
            }
        });
        let action = ret.body.toString('utf8').split(" ");
        if (action[0] == "move") {
            // move returned
            console.log("EliteFourBot condition: \n", ourCondition)
            console.log("Opponent condition: ", foePokemon.hp)
            console.log("Bot condition: ", ourPokemon.hp)
            console.log("Baseline Move: ", decision[0].move)

            let newDecision = decisions.filter(decision => 
                decision[0].type == 'move' &&
                formatName(decision[0].move) == action[1]
            )[0]
            console.log("Minimax Move: ", newDecision[0].move)

            return newDecision
        } else if (action[0] == "switch") {
            // switch returned
            let nextPokemon = decisions.filter(decision => 
                decision[0].type == 'switch' &&
                formatName(decision.poke.split(" ")[1]) == action[1]
            )
            if (nextPokemon.length != 0) {
                console.log(nextPokemon)
                return nextPokemon[0]
            }
        } else {
            for (var property in foePokemon){
                console.log(property + ": " + foePokemon[property]);
            }
            console.log("ERROR IN minimaxserver.py. ACTION NOT RETURNED")
            console.log({
                generation: GEN,
                currPokemon: POKEDEX[ourName].num,
                ourPokemon: ourPokedexNumbers,
                theirPokemon: POKEDEX[foeName].num,
                ourHp: ourCondition,
                theirHp: foePokemon.hp/100,
                theirStatus: foePokemon.status,
                ourMoves: ourMoves,
                theirMoves: theirMoves,
                ourStats: ourBaseStats,
                ourLevel: ourPokemon.level,
                theirLevel: foePokemon.level,
                ourTypes: ourTypes,
                theirTypes: foePokemon.template.types,
                ourBaseStats: ourPokemon.template.baseStats,
                theirBaseStats: foePokemon.template.baseStats,
                ourBoosts: ourPokemon.boosts,
                theirBoosts: foePokemon.boosts
            })
        }
    } catch (error) {
        console.log(error)
    }

    console.log("BASELINE MOVE RETURNED")

    // If no viable moves, choose any move
    if (decision.length == 0) {
        let viableMoves = decisions.filter(decision => decision[0].type == 'move')
        return viableMoves[viableMoves.length > 0 ? Math.floor(Math.random() * viableMoves.length-1): 0]
    }

    // turn++
    // If try-catch fails, choose baseline move
    return decision
}

var getBestSwitch = exports.getBestSwitch = (battle, decisions) => {
    let foePokemon = battle.foe.pokemon[0].species
    let foeName = formatName(foePokemon)
    turn++
    
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
 
    let moveDamage = []
    for (let move of moves) {
        let moveName = formatName(move.move)
        // console.log(moveName)
        // Handle edge case causing crashes
        if (moveName == 'return102') {
            moveName = 'return'
        }
        var damage = 0
        let level = Number(battle.self.pokemon[0].level)
        let attack = getAttackStat(attacker, moveName)
        let basePower = Number(MOVES[moveName].basePower)
        let defense = getDefenseStat(defender, moveName)
        let sameType = sameTypeMultiplier(attacker, moveName)
        let attackType = attackTypeMultiplier(defender, moveName)
        let randomNum = getRandomInt(217, 255+1)
        if (move.hasOwnProperty("status")) {
            damage = -1
        } else {
            damage = ((((2 * level / 5 + 2) * attack / defense) / 50) + 2) * (sameType * attackType * randomNum)
        }
        moveDamage.push([damage, move])
    }

    // console.log("calculateDamage SUCCESS")
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
