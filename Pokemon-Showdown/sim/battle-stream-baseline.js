/**
 * Battle Stream Example
 * Pokemon Showdown - http://pokemonshowdown.com/
 *
 * Example of how to create AIs battling against each other.
 *
 * @license MIT
 * @author Guangcong Luo <guangcongluo@gmail.com>
 */
 
'use strict';
 
const BattleStreams = require('./battle-stream');
const Dex = require('./dex');
const POKEDEX = require('../data/pokedex').BattlePokedex
const TYPES = require('../data/typechart').BattleTypeChart
const SPECIAL_CHARS = /[%\s\.'-]/g

var randomBotPokemon = ''
var baselineBotPokemon = ''
var fainted = 0
 
/*********************************************************************
 * Helper functions
 *********************************************************************/
 
/**
 * @param {number[]} array
 */
function randomElem(array) {
    return array[Math.floor(Math.random() * array.length)];
}

function getPokemonName(pokemon) {
    return pokemon.details.split(", ")[0].toLowerCase().replace(SPECIAL_CHARS, "")
}
 
/*********************************************************************
 * Define AI
 *********************************************************************/
 
class RandomPlayerAI extends BattleStreams.BattlePlayer {
    /**
     * @param {AnyObject} request
     */
    receiveRequest(request) {
        if (request.wait) {
            // wait request
            // do nothing
        } else if (request.forceSwitch) {
            // switch request
            const pokemon = request.side.pokemon;
            let chosen = /** @type {number[]} */ ([]);
            const choices = request.forceSwitch.map((/** @type {AnyObject} */ mustSwitch) => {
                if (!mustSwitch) return `pass`;
                let canSwitch = [1, 2, 3, 4, 5, 6];
                canSwitch = canSwitch.filter(i => (
                    // not active
                    i > request.forceSwitch.length &&
                    // not chosen for a simultaneous switch
                    !chosen.includes(i) &&
                    // not fainted
                    !pokemon[i - 1].condition.endsWith(` fnt`)
                ));
                const target = randomElem(canSwitch);
                chosen.push(target);
                return `switch ${target}`;
            });
            this.choose(choices.join(`, `));
        } else if (request.active) {
            randomBotPokemon = request.side.pokemon.filter((pokemon) => {
                return pokemon.active
            })[0]
            // move request
            const choices = request.active.map((/** @type {AnyObject} */ pokemon, /** @type {number} */ i) => {
                if (request.side.pokemon[i].condition.endsWith(` fnt`)) return `pass`;
                let canMove = [1, 2, 3, 4].slice(0, pokemon.moves.length);
                canMove = canMove.filter(i => (
                    // not disabled
                    !pokemon.moves[i - 1].disabled
                ));
                const move = randomElem(canMove);
                const targetable = request.active.length > 1 && ['normal', 'any'].includes(pokemon.moves[move - 1].target);
                const target = targetable ? ` ${1 + Math.floor(Math.random() * 2)}` : ``;
                return `move ${move}${target}`;
            });
            this.choose(choices.join(`, `));
        } else {
            // team preview?
            this.choose(`default`);
        }
    }
}
 
 
/*********************************************************************
 * Define Baseline AI
 *********************************************************************/
 
class BaselinePlayerAI extends BattleStreams.BattlePlayer {
    /**
     * @param {AnyObject} request
     */
    receiveRequest(request) {
        if (request.wait) {
            // wait request
            // do nothing
        } else if (request.forceSwitch) {
            fainted++
            console.log("FAINTED", fainted)
            // switch request
            const pokemon = request.side.pokemon;
            let chosen = /** @type {number[]} */ ([]);
            const choices = request.forceSwitch.map((/** @type {AnyObject} */ mustSwitch) => {
                if (!mustSwitch) return `pass`;
 
                // Get available pokemon sorted by level
                let availablePokemon = pokemon.map((pokemon, i) => {
                    pokemon['index'] = i + 1
                    return pokemon
                }).filter(pokemon => (
                    // not active
                    // pokemon.index + 1 > request.forceSwitch.length &&
                    pokemon.active != true &&
                    // not chosen for a simultaneous switch
                    !chosen.includes(pokemon.index) &&
                    // not fainted
                    !pokemon.condition.endsWith(` fnt`)
                )).sort(function(a, b) {
                    let high = Number(b.details.split(", ")[1].substring(1))
                    let low = Number(a.details.split(", ")[1].substring(1))
                    return low - high
                })
 
                if (randomBotPokemon != '') {
                    // choose pokemon that fares well against enemy type
                    let opponent = getPokemonName(randomBotPokemon)
                    let damageTaken = []
 
                    // Get damage by types
                    for (let entry of POKEDEX[opponent]['types']) {
                        for (let pokeType in TYPES[entry]['damageTaken']) {
                            if (TYPES[entry]['damageTaken'][pokeType] != 0) {
                                damageTaken.push([pokeType, TYPES[entry]['damageTaken'][pokeType]])
                            }
                        }
                    }
                    damageTaken.sort(function(a, b) { b[1] - a[1] })
 
                    for (let pokeType of damageTaken) {
                        for (let bestPokemon of availablePokemon) {
                            if (POKEDEX[getPokemonName(bestPokemon)].types.includes(pokeType[0])) {
                                const target = bestPokemon.index
                                baselineBotPokemon = pokemon[target - 1]
                                chosen.push(target);
                                return `switch ${target}`;
                            }
                        }
                    }
                }
 
                const target = availablePokemon[availablePokemon.length > 1? Math.round(Math.random()): 0].index
                // baselineBotPokemon = pokemon[target - 1]
                chosen.push(target);
                return `switch ${target}`;
            });
            this.choose(choices.join(`, `));
        } else if (request.active) {
            // move request
            baselineBotPokemon = request.side.pokemon.filter((pokemon) => {
                return pokemon.active
            })[0]
            const choices = request.active.map((/** @type {AnyObject} */ pokemon, /** @type {number} */ i) => {
                if (request.side.pokemon[i].condition.endsWith(` fnt`)) return `pass`;
 
                // Get sorted, valid moves
                let moves = pokemon.moves.map((move, i) => {
                    move['index'] = i + 1
                    return move
                }).filter(move => (!move.disabled)).sort(function(a, b) {
                    return a.maxpp - b.maxpp
                })
 
                let move = moves[moves.length > 1? Math.round(Math.random()): 0].index
                const targetable = request.active.length > 1 && ['normal', 'any'].includes(pokemon.moves[move - 1].target);
                const target = targetable ? ` ${1 + Math.floor(Math.random() * 2)}` : ``;
                return `move ${move}${target}`;
            });
            this.choose(choices.join(`, `));
        } else {
            // team preview?
            this.choose(`default`);
        }
    }
}

 
/*********************************************************************
 * Run AI
 *********************************************************************/
 
for (var i = 0; i < 100; i++) {
const streams = BattleStreams.getPlayerStreams(new BattleStreams.BattleStream());
 
const spec = {
    formatid: "gen1customgame",
};
const p1spec = {
    name: "Random Bot",
    team: Dex.packTeam(Dex.generateTeam('gen1randombattle')),
};
const p2spec = {
    name: "Baseline Bot",
    team: Dex.packTeam(Dex.generateTeam('gen1randombattle')),
};
 
// eslint-disable-next-line no-unused-vars
const p1 = new RandomPlayerAI(streams.p1);
// eslint-disable-next-line no-unused-vars
const p2 = new BaselinePlayerAI(streams.p2);
 
(async () => {
    let chunk;
    while ((chunk = await streams.omniscient.read())) {
        console.log(chunk);
    }
})();
 
streams.omniscient.write(`>start ${JSON.stringify(spec)}
>player p1 ${JSON.stringify(p1spec)}
>player p2 ${JSON.stringify(p2spec)}`);
}