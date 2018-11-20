import json
import numpy as np
from deepx.nn import *
from deepx.optimizer import Adam


def readJSON(filename):
	'''Helper function to read JSON files'''
	with open(filename) as f:
	    read_data = f.read()
	f.closed
	return json.loads(read_data)

	


def train(turns, iters = 10000, batch_size=200):
	adam = Adam(loss)
	learning_rate = 0.0001
	idx = np.arange(len(turns))	
	avg_loss = 0
	exs = np.random.permutation(turns)
	for i in range(iters):
		ix = np.random.choice(idx) #randomly select turn from JSON_file
		es = exs[ix: ix + batch_size] #select the next forty or so turns for small batch learning
		X = np.stack([e[0] for e in es], axis=0)
		y = np.stack([e[1] for e in es], axis=0)
		loss = adam.train(X, y, learning_rate)
		if avg_loss == 0:
			avg_loss = loss
		else:
			avg_loss = avg_loss * 0.90 + 0.10 * loss
	return adam
turns = readJSON("features.json")
turns = np.array(turns)
model = train(turns)




