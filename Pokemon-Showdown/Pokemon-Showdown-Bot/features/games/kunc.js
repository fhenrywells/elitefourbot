/*
	Kunc
*/

var Kunc = require('./constructors.js').Kunc;
var RandomGenerator = require('./kunc-rand.js');

function send (room, str) {
	Bot.say(room, str);
}

function trans (data, room) {
	var lang = Config.language || 'english';
	if (Settings.settings['language'] && Settings.settings['language'][room]) lang = Settings.settings['language'][room];
	return Tools.translateGlobal('games', 'kunc', lang)[data];
}

function parseWinners (winners, room) {
	var res = {
		type: 'win',
		text: "**" + winners[0] + "**"
	};
	if (winners.length < 2) return res;
	res.type = 'tie';
	for (var i = 1; i < winners.length - 1; i++) {
		res.text += ", **" + winners[i] + "**";
	}
	res.text += " " + trans('and', room) + " **" + winners[winners.length - 1] + "**";
	return res;
}

exports.id = 'kunc';

exports.title = 'Kunc';

exports.aliases = [];

var parser = function (type, data) {
	var txt;
	switch (type) {
		case 'start':
			txt = trans('start', this.room);
			if (this.maxGames) txt += ". " + trans('maxgames1', this.room) + " __" + this.maxGames + " " + trans('maxgames2', this.room) + "__";
			if (this.maxPoints) txt += ". " + trans('maxpoints1', this.room) + " __" + this.maxPoints + " " + trans('maxpoints2', this.room) + "__";
			txt += ". " + trans('timer1', this.room) + " __" + Math.floor(this.answerTime / 1000).toString() + " " + trans('timer2', this.room) + "__";
			txt += ". " + trans('help', this.room).replace("$TOKEN", CommandParser.commandTokens[0]);
			send(this.room, txt);
			break;
		case 'show':
			send(this.room, "**" + exports.title + ":** " + trans('q', this.room) + ": __" + this.moves.join(', ') + "__" + (this.tierclue ? (" | Tier: " + this.tierclue) : ''));
			break;
		case 'point':
			send(this.room, trans('grats1', this.room) + " **" + data.user + "** " + trans('point2', this.room) + " __" + this.pokemon + "__. " + trans('point3', this.room) + ": " + data.points + " " + trans('points', this.room));
			break;
		case 'timeout':
			send(this.room, trans('timeout', this.room) + " __" + this.pokemon.trim() + "__");
			break;
		case 'end':
			send(this.room, trans('lose', this.room));
			break;
		case 'win':
			var t = parseWinners(data.winners, this.room);
			txt = "**" + trans('end', this.room) + "** ";
			switch (t.type) {
				case 'win':
					txt += trans('grats1', this.room) + " " + t.text + " " + trans('grats2', this.room) + " __" + data.points + " " + trans('points', this.room) + "__!";
					break;
				case 'tie':
					txt += trans('tie1', this.room) + " __" + data.points + " " + trans('points', this.room) + "__ " + trans('tie2', this.room) + " " + t.text;
					break;
			}
			send(this.room, txt);
			break;
		case 'forceend':
			send(this.room, trans('forceend1', this.room) + (this.status === 2 ? (" " + trans('forceend2', this.room) + " __" + this.pokemon.trim() + "__") : ''));
			break;
		case 'error':
			send(this.room, "**" + exports.title + ": Error (could not fetch a word)");
			this.end(true);
			break;
	}
	if (type in {win: 1, end: 1, forceend: 1}) {
		Features.games.deleteGame(this.room);
	}
};

var wordGenerator = function (arr) {
	return RandomGenerator.randomNoRepeat(arr);
};

exports.newGame = function (room, opts) {
	if (!RandomGenerator.random()) return null;
	var generatorOpts = {
		room: room,
		title: exports.title,
		maxGames: 5,
		maxPoints: 0,
		waitTime: 2 * 1000,
		answerTime: 30 * 1000,
		wordGenerator: wordGenerator
	};
	var temp;
	for (var i in opts) {
		switch (i) {
			case 'ngames':
			case 'maxgames':
			case 'games':
				temp = parseInt(opts[i]) || 0;
				if (temp && temp < 0) return "games ( >= 0 ), maxpoints, time";
				generatorOpts.maxGames = temp;
				break;
			case 'points':
			case 'maxpoints':
				temp = parseInt(opts[i]) || 0;
				if (temp && temp < 0) return "games, maxpoints ( >= 0 ), time";
				generatorOpts.maxPoints = temp;
				break;
			case 'answertime':
			case 'anstime':
			case 'time':
				temp = parseFloat(opts[i]) || 0;
				if (temp) temp *= 1000;
				if (temp && temp < (5 * 1000)) return "games, maxpoints, time ( seconds, >= 5 )";
				generatorOpts.answerTime = temp;
				break;
			default:
				return "games, maxpoints, time";
		}
	}
	if (!generatorOpts.maxGames && !generatorOpts.maxPoints) generatorOpts.maxGames = 5;
	var game = new Kunc(generatorOpts, parser);
	if (!game) return null;
	game.generator = exports.id;
	return game;
};

exports.commands = {
	gword: 'g',
	guess: 'g',
	g: function (arg, by, room, cmd, game) {
		if (cmd !== 'gword') {
			try {
				var aliases = require("./../../data/aliases.js").BattleAliases;
				if (aliases[toId(arg)]) arg = aliases[toId(arg)];
			} catch (e) {
				debug(e.stack);
			}
		}
		game.guess(by.substr(1), arg);
	},
	view: function (arg, by, room, cmd, game) {
		if (game.status < 2) return;
		this.restrictReply("**" + exports.title + ":** " + trans('q', this.room) + ": __" + game.moves.join(', ') + "__" + (game.tierclue ? (" | Tier: " + game.tierclue) : ''), 'games');
	},
	end: 'endkunc',
	endkunc: function (arg, by, room, cmd, game) {
		if (!this.can('games')) return;
		game.end(true);
	}
};
