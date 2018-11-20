import subprocess
from multiprocessing.dummy import Pool

ourWin = 0
numTrials = 100


def runBattle(_):
  out = subprocess.Popen(['node', 'battle-stream-example.js'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
  stdout, stderr = out.communicate()
  print(str(stdout).split("\\n")[-2])
  return(str(stdout).split("\\n")[-2])


p = Pool(50)
results = p.map(runBattle, range(numTrials))
print(results)
for result in results:
  if "Baseline Bot" in result:
    ourWin = ourWin + 1

print(float(ourWin) / float(numTrials))
