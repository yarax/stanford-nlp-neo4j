import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from brain import analyze

graph = {"nodes":[{"id":"103","labels":["man"],"properties":{}},{"id":"105","labels":["I"],"properties":{}},{"id":"109","labels":["person"],"properties":{}}],"relationships":[{"id":"131","type":"class","startNode":"105","endNode":"103","properties":{}},{"id":"137","type":"class","startNode":"103","endNode":"109","properties":{}}]}

res = analyze.sort_nodes(graph)
print res


res = analyze.get_possible_chains(3)
print res