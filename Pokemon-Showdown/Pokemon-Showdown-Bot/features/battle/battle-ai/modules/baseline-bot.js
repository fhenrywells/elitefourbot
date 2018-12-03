const POKEDEX = require('../../../../../data/pokedex').BattlePokedex
const TYPES = require('../../../../../data/typechart').BattleTypeChart
const SPECIAL_CHARS = /[%\s\.'-]/g

// var fainted = 0

var getBestMove = exports.getBestMove = (battle, decisions) => {
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
        return high - low
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
    damageTaken.sort(function(a, b) {
        return b[1] - a[1]
    })

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

var formatName = (pokemon) => {
    return pokemon.toLowerCase().replace(SPECIAL_CHARS, "")
}
var getPokemonName = (pokemon) => {
    return pokemon.details.split(", ")[0].toLowerCase().replace(SPECIAL_CHARS, "")
}