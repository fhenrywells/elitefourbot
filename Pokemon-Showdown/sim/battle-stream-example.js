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
 
/*********************************************************************
 * Helper functions
 *********************************************************************/
 
/**
 * @param {number[]} array
 */
function randomElem(array) {
    return array[Math.floor(Math.random() * array.length)];
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
 * Run AI
 *********************************************************************/
 
for (var i = 0; i < 100; i++) {
const streams = BattleStreams.getPlayerStreams(new BattleStreams.BattleStream());
 
const spec = {
    formatid: "gen7customgame",
};
const p1spec = {
    name: "Human Bot",
    team: Dex.packTeam(Dex.generateTeam('gen1randombattle')),
};
const p2spec = {
    name: "Baseline Bot",
    team: Dex.packTeam(Dex.generateTeam('gen1randombattle')),
};
 
// eslint-disable-next-line no-unused-vars
const p1 = new HumanPlayer(streams.p1);
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