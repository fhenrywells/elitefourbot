/*
 * Battle Stream Example
 * Pokemon Showdown - http://pokemonshowdown.com/
 *
 * Example of how to create AIs battling against each other.
 *
 * @license MIT
 * @author Guangcong Luo <guangcongluo@gmail.com>
 */
 
'use strict';
var requestapi = require('sync-request');

const BattleStreams = require('./battle-stream');
const Dex = require('./dex');
const TypeChart = require('../data/typechart')
const TYPES = TypeChart.BattleTypeChart
const SPECIAL_CHARS = /[%\s\.'-]/g
 
var randomBotPokemon = ''
var baselineBotPokemon = ''
var minimaxBotPokemon = ''
var ourBaseStats = new Object()
var theirBaseStats = new Object()
 
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
 
function getPokemonLevel(pokemon) {
    return pokemon.details.split(", ")[1].slice(1)
}
 
function getSpecies(pokemon) {
    return POKEDEX[getPokemonName(pokemon)].species
}
 
function calculateDamage(attacker, defender, moves) {
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
 
    let moveDamage = []
    for (let move of moves) {
        let moveName = move.move.toLowerCase().replace(SPECIAL_CHARS, "")
        // Handle edge case causing crashes
        if (moveName == 'return102') {
            moveName = 'return'
        }
        var damage = 0
        let level = getPokemonLevel(attacker)
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
 
    return moveDamage
 
}
 
function getAttackStat(attacker, move) {
    let attack = 0
    if (MOVES[move] == null) {
        return 0
    }
    if (MOVES[move].category == "Special") {
        attack = attacker.stats.spa
    } else if (MOVES[move].category == "Physical") {
        attack = attacker.stats.atk
    } else {
        // console.log("!!! HANDLE THIS CASE !!! : ", move, MOVES[move])
        attack = attacker.stats.atk
    }
 
    return Number(attack)
}
 
function getDefenseStat(defender, move) {
    let defense = 0
    if (MOVES[move] == null) {
        return 0
    }
    if (MOVES[move].category == "Special") {
        defense = defender.stats.spd
    } else if (MOVES[move].category == "Physical") {
        defense = defender.stats.def
    } else {
        // console.log("!!! HANDLE THIS CASE !!! : ", move, MOVES[move])
        defense = defender.stats.def
    }
 
    return Number(defense)
}
 
function sameTypeMultiplier(attacker, move) {
    if (POKEDEX[getPokemonName(attacker)].types.includes(MOVES[move].type)) {
        return 1.5
    }
    return 1
}
 
function attackTypeMultiplier(defender, move) {
    let damageTaken = 1
 
    for (let pokeType of POKEDEX[getPokemonName(defender)].types) {
        damageTaken *= Number(TYPES[pokeType].damageTaken[MOVES[move].type])
    }
 
    return Number(damageTaken)
}
 
function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return min + Math.floor(Math.random() * (max - min + 1));
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
                // randomBotPokemon = pokemon[target - 1]
                chosen.push(target);
                return `switch ${target}`;
            });
            //console.log("Choices are ", choices)
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
                    a.details.split(", ")[1] - b.details.split(" ")[1]
                })
 
                if (minimaxBotPokemon != '') {
                    // choose pokemon that fares well against enemy type
                    let opponent = getPokemonName(minimaxBotPokemon)
                    let damageTaken = []
 
                    // Get damage by types
                    for (let entry of POKEDEX[opponent]['types']) {
                        for (let pokeType in TYPES[entry]['damageTaken']) {
                            if (TYPES[entry]['damageTaken'][pokeType] != 0) {
                                damageTaken.push([pokeType, TYPES[entry]['damageTaken'][pokeType]])
                            }
                        }
                    }
                    damageTaken.sort(function(a, b) { a[1] - b[1] })
 
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
                //console.log("baseline moves are ", moves)
                let move = moves[moves.length > 1? Math.round(Math.random()): 0].index
                //console.log("baseline move is ", move)
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
 * Define Human Player
 *********************************************************************/
 
class HumanPlayer extends BattleStreams.BattlePlayer {
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
            // move request
            let pokemon = request.active[0]
            let validMoves = [1, 2, 3, 4].slice(0, pokemon.moves.length).filter(i => (
                // not disabled
                !pokemon.moves[i - 1].disabled
            ));
 
            // Prompt user for input
            console.log("\nChoose your move: ")
            validMoves.forEach(move => console.log(move, pokemon.moves[move - 1]))
 
            // Choose specified move
            prompt((input) => {
                const choices = request.active.map((/** @type {AnyObject} */ pokemon, /** @type {number} */ i) => {
                    if (request.side.pokemon[i].condition.endsWith(` fnt`)) return `pass`;
 
                    let move = input
                    const targetable = request.active.length > 1 && ['normal', 'any'].includes(pokemon.moves[move - 1].target);
                    const target = targetable ? ` ${1 + Math.floor(Math.random() * 2)}` : ``;
 
                    return `move ${move}${target}`;
                });
                this.choose(choices.join(`, `));
            })
            console.log('\n')
        } else {
            // team preview?
            this.choose(`default`);
        }
 
         
        function prompt(callback) {
            var stdin = process.stdin,
                stdout = process.stdout;
 
            stdin.resume();
            // stdout.write(question);
 
            stdin.once('data', function (data) {
                callback(data.toString().trim());
            });
        }
    }
}
 
 
/*********************************************************************
 * Define AI Player
 *********************************************************************/
 
class MinimaxPlayerAI extends BattleStreams.BattlePlayer {
    /**
     * @param {AnyObject} request
     */
    receiveRequest(request) {
        if (request.wait) {
            // wait request
            // do nothing
        } else if (request.forceSwitch) {
            // switch request
            turn += 1
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
                    pokemon.active != true &&
                    // pokemon.index + 1 > request.forceSwitch.length &&
                    // not chosen for a simultaneous switch
                    !chosen.includes(pokemon.index) &&
                    // not fainted
                    !pokemon.condition.endsWith(` fnt`)
                )).sort(function(a, b) {
                    a.details.split(", ")[1] - b.details.split(" ")[1]
                })
                

                if (baselineBotPokemon != '') {
                    // choose pokemon that fares well against enemy type
                    let opponent = getPokemonName(baselineBotPokemon)
                    let damageTaken = []
                    // Get damage by types
                    for (let entry of POKEDEX[opponent]['types']) {
                        for (let pokeType in TYPES[entry]['damageTaken']) {
                            if (TYPES[entry]['damageTaken'][pokeType] != 0) {
                                damageTaken.push([pokeType, TYPES[entry]['damageTaken'][pokeType]])
                            }
                        }
                    }
                    damageTaken.sort(function(a, b) { a[1] - b[1] })
 
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
                baselineBotPokemon = pokemon[target - 1]
                chosen.push(target);
                return `switch ${target}`;
            });
            this.choose(choices.join(`, `));
        } else if (request.active) {
            // move request
            minimaxBotPokemon = request.side.pokemon.filter((pokemon) => {
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

                // Damage calculated for each move
                //let damageCalculator = calculateDamage(minimaxBotPokemon, baselineBotPokemon, moves)
                //console.log("DAMAGE", damageCalculator)

                let move = moves[moves.length > 1? Math.round(Math.random()): 0].index
                const targetable = request.active.length > 1 && ['normal', 'any'].includes(pokemon.moves[move - 1].target);
                const target = targetable ? ` ${1 + Math.floor(Math.random() * 2)}` : ``;

                //var damageArray = new Object()
                //for (i = 0; i < damageCalculator.length; i++) {
                //    damageArray[damageCalculator[i][1]['id']] = damageCalculator[i][0]
                //}

                let theirMoves = FORMATSDATA[getPokemonName(baselineBotPokemon)]['randomBattleMoves']
                var essentialMove = FORMATSDATA[getPokemonName(baselineBotPokemon)]['essentialMove']
                if (typeof(essentialMove) === 'undefined') {
                    //console.log("undefined")
                } else {
                    theirMoves = theirMoves.concat(essentialMove)
                }
                
                var exclusiveMoves = FORMATSDATA[getPokemonName(baselineBotPokemon)]['exclusiveMoves']

                if (typeof(exclusiveMoves) === 'undefined') {
                    //console.log("undefined")
                } else {
                    theirMoves = theirMoves.concat(exclusiveMoves)
                }

               /* var theirMoves = new Array(theirMoveNames.length)
                for (i = 0; i < theirMoveNames.length; i++) {
                    theirMoves[i] = MOVES[theirMoveNames[i]]
                    theirMoves[i].move = theirMoves[i].name
                }*/
                /*
                let theirDamageCalculator = calculateDamage(baselineBotPokemon, minimaxBotPokemon, theirMoves)

                var theirDamageArray = new Object()
                for (i = 0; i < theirDamageCalculator.length; i++) {
                    theirDamageArray[theirDamageCalculator[i][1]['id']] = theirDamageCalculator[i][0]
                }
                */
                

                var ourCondition= new Object()
                var ourStats = new Object()
                var ourMoves = new Object()
                var ourDetails = new Object()
                var ourTypes = new Object()
                var ourPokemon = new Object()
                var ourPokemonIndices = new Object()

                //console.log("size of team is", request.side.pokemon.length)
                for (i = 0; i < request.side.pokemon.length; i++) {
                    var pokedexNum = POKEDEX[getPokemonName(request.side.pokemon[i])].num
                    ourCondition[pokedexNum] = request.side.pokemon[i].condition
                    ourStats[pokedexNum] = request.side.pokemon[i].stats
                    ourMoves[pokedexNum] = request.side.pokemon[i].moves
                    ourDetails[pokedexNum] = request.side.pokemon[i].details
                    ourTypes[pokedexNum] = POKEDEX[getPokemonName(request.side.pokemon[i])].types
                    ourPokemon[pokedexNum] = pokedexNum
                    ourPokemonIndices[pokedexNum] = i + 1
                    if (pokedexNum == POKEDEX[getPokemonName(minimaxBotPokemon)].num){
                        var moveList = new Array()
                        //console.log("moves are ", moves)
                        for (var j = 0; j < moves.length; j ++) {
                            //console.log("move state is ", moves[j].disabled)
                            if(moves[j].disabled == false) {
                                moveList.push(moves[j].id)
                            } 
                        }
                        ourMoves[pokedexNum] = moveList
                    }
                }
                //console.log("our stats are ",ourStats) 
                if (POKEDEX[getPokemonName(baselineBotPokemon)].num in theirBaseStats) {
                    //console.log("seen this poke before")
                } else {
                    theirBaseStats[POKEDEX[getPokemonName(baselineBotPokemon)].num] = baselineBotPokemon.stats
                }

                if (turn == 1){
                    //var ourBaseStats = 
                    //console.log("base stats set!")
                    ourBaseStats = JSON.parse(JSON.stringify(ourStats));

                } //implement proper basestat module 
                const choices = request.active.map((/** @type {AnyObject} */ pokemon, /** @type {number} */ i) => {
                //console.log("our base stats are ",ourBaseStats) 

                if (moves.length == 1){ //handles recharge moves 
                    return ("move " + moves[0].id)
                }

                var ret = requestapi('POST', 'http://127.0.0.1:5000/getaction', {
                    json: {
                        generation: gen,
                        currPokemon: POKEDEX[getPokemonName(minimaxBotPokemon)].num,
                        ourPokemon: ourPokemon,
                        theirPokemon: POKEDEX[getPokemonName(baselineBotPokemon)].num,
                        ourHp: ourCondition,
                        theirHp: baselineBotPokemon.condition,
                        ourMoves: ourMoves,
                        theirMoves: theirMoves,
                        ourStats: ourStats,
                        theirStats : baselineBotPokemon.stats,
                        ourDetails: ourDetails,
                        theirDetails: baselineBotPokemon.details,
                        ourTypes: ourTypes,
                        theirTypes: POKEDEX[getPokemonName(baselineBotPokemon)].types,
                        ourBaseStats: ourBaseStats,
                        theirBaseStats: theirBaseStats
                    }
                });
                var action = ret.body.toString('utf8');
                if (action.startsWith("switch")) {
                    pokedexNum = action.split(" ")[1];
                    action = "switch " + ourPokemonIndices[pokedexNum];
                }
                //console.log("ret is ", ret.body.toString('utf8'))
                return action
                //return `move ${move}${target}`;
            });
                this.choose(choices.join(`, `));
            })
            console.log('\n')
        } else {
            // team preview?
            this.choose(`default`);
        }
        turn += 1
    }
}
 
 
/*********************************************************************
 * Run AI
 *********************************************************************/
 
const streams = BattleStreams.getPlayerStreams(new BattleStreams.BattleStream());
 
const gen = "gen1"
const formid = gen + 'customgame'

const spec = {
    formatid: formid,
};


const FormatDataFile = '../mods/' + gen + "/formats-data.js"
const FormatsData = require(FormatDataFile)
const FORMATSDATA = FormatsData.BattleFormatsData
const MovesDataFile = '../mods/' + gen + "/moves.js"
const Moves = require(MovesDataFile)
const MOVES = Moves.BattleMovedex
const PokedexFile = '../mods/' + gen + "/pokedex.js"
const Pokedex = require(PokedexFile)
const POKEDEX = Pokedex.BattlePokedex

var turn = 0

//for (var i = 0; i < 10; i++) {


const battleType = gen + "randombattle"

const p1spec = {
    name: "Baseline Bot",

    team: Dex.packTeam(Dex.generateTeam(battleType)),
};
const p2spec = {
    name: "Minimax Bot",
    team: Dex.packTeam(Dex.generateTeam(battleType)),
};



const team = Dex.fastUnpackTeam(p2spec.team)
//console.log("team is ", team)
var turn = 1;

// eslint-disable-next-line no-unused-vars
const p1 = new BaselinePlayerAI(streams.p1);
// eslint-disable-next-line no-unused-vars
const p2 = new MinimaxPlayerAI(streams.p2);
//console.log(Dex.fastUnpackTeam(p2spec.team))

 
(async () => {
    let chunk;
    while ((chunk = await streams.omniscient.read())) {
        console.log(chunk);
    }
})();
 
streams.omniscient.write(`>start ${JSON.stringify(spec)}
>player p1 ${JSON.stringify(p1spec)}
>player p2 ${JSON.stringify(p2spec)}`);
//}