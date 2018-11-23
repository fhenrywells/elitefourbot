import json
from pprint import pprint

with open("formats-data.json") as f:
    formats_data = json.loads(f.read())

with open("moves.json") as f:
    moves = json.loads(f.read())

with open("movesall.json") as f:
    moves_all = json.loads(f.read())

viable_moves = []

for k, v in formats_data.items():
    viable_moves += v.get('randomBattleMoves', [])
    if v.get('essentialMove', None) is not None:
        viable_moves.append(v.get('essentialMove'))
    viable_moves += v.get('exclusiveMoves', [])

viable_moves = list(set(viable_moves))
viable_moves_data = {}
for move in viable_moves:
    if move in moves.keys():
        gen1_move_data = moves[move]
        move_data = moves_all[move]
        if 'inherit' in gen1_move_data.keys() and gen1_move_data['inherit']:
            total_move_data = move_data
            for k, v in gen1_move_data.items():
                total_move_data[k] = v
        else:
            total_move_data = gen1_move_data
    else:
        total_move_data = moves_all[move]
    viable_moves_data[move] = total_move_data

pprint(viable_moves_data)
with open("viablemovesdata.json", "w") as f:
    json.dump(viable_moves_data, f, indent=4, sort_keys=True)