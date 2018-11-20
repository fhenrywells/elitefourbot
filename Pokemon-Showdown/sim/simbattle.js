const Sim = require('Pokemon-Showdown/sim');
stream = new Sim.BattleStream();

(async () => {
    let output;
    while ((output = await stream.read())) {
        console.log(output);
    }
})();

stream.write(`>start {"formatid":"gen7randombattle"}`);
stream.write(`>player p1 {"name":"Alice"}`);
stream.write(`>player p2 {"name":"Bob"}`);