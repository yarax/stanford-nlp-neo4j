# Description:
# Node name is a label (:word)
# Relationships have label/type
# Relations types:
#   - part of speech stanford nlp
#   - context
#   - time?
#   - place?
#   - class (obj1 belongs to class obj2)
#   - method ?
# @TODO
# incapsulate each phrase ROOT and link it with context

"""
trees are green
birch is a tree
what color is birch?
"""
import time
import json
from neo4jrestclient.client import GraphDatabase
from nltk.stem.wordnet import WordNetLemmatizer

gdb = GraphDatabase("http://localhost:7474/db/data/", username="neo4j", password="123")

from stanford_corenlp_python import jsonrpc
from simplejson import loads
server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(),
                             jsonrpc.TransportTcpIp(addr=("127.0.0.1", 3456)))


RELATION_TYPES = {
	"class" : "class"
}

def check_lemma_relations(origin, lemma, pos):
	# plural is a "class" relation
	if pos == "NNS":
		q = "MATCH (a:{0}), (b:{1}) MERGE a-[rel:class]->b".format(lemma, origin)
		gdb.query(q = q)


def check_lemmas(words):
	for i, word in enumerate(words):
		lemma = word[1]["Lemma"].lower()
		origin = word[0].lower()
		pos = word[1]["PartOfSpeech"]

		if (lemma != origin):
			q = "MERGE (a:{0})".format(lemma)
			gdb.query(q = q)
			# Origin should be already created
			q = "MATCH (a:{0}), (b:{1}) MERGE a-[rel:lemma {{pos: '{2}'}}]->b".format(origin, lemma, pos)
			gdb.query(q = q)
			check_lemma_relations(origin, lemma, pos)


def check_class_relations(dependencies):
	for dep in dependencies:
		if (dep[0] == "nsubj"):
			q = "MATCH (a:{0}), (b:{1}) MERGE a-[rel:{2}]->b".format(dep[2], dep[1], RELATION_TYPES["class"])
			gdb.query(q = q)


def save_dependencies(dependencies):
	for dep in dependencies:
		# @TODO Store normal form?
		obj = dep[2]
		depon = dep[1]
		type = dep[0]
		if (depon == "ROOT"):
			depon = "SCOPE" + str(int(time.time()))
			root = depon

		q = "MERGE (a:{0})".format(obj)
		gdb.query(q = q)
		q = "MERGE (a:{0})".format(depon)
		gdb.query(q = q)
		q = "MATCH (a:{0}), (b:{1}) MERGE a-[rel:{2} {{ scope: '{3}' }}]->b".format(obj, depon, type, context)
		#print q
		gdb.query(q = q)
		# Link scope with pointed context
		#q = "MATCH (a:{0}), (b:{1}) MERGE a-[rel:{2}]->b".format(root, context, RELATION_TYPES["class"])
		#print q
		#gdb.query(q = q)

# @TODO TESTS!! refactor global places
def find_implicit_relations():
	places = []
	node_hash = {}
	def place_nodes(child, parent):
		try:
			ch_i = places.index(child)
			places[ch_i + 1] = parent
		except:
			try:
				par_i = places.index(parent)
				places.insert(par_i, child)
			except:
				places.append(child)
				place_nodes(child, parent)

	def not_neighbors():
		nn = []
		for i in range(0, len(places)):
			for j in range(i+2, len(places)):
				nn.append([places[i], places[j]])
		return nn

	q = "MATCH (a)-[r:class]-(b) RETURN a, b, r"
	res = gdb.query(q = q, data_contents=True)
	#print json.dumps(res.graph)
	for i, nodes in enumerate(res.graph):
		# fucking crutch
		if i % 2 == 1:
			continue
		for node in nodes["nodes"]:
			node_hash[node["id"]] = node["labels"][0]
		rel = nodes["relationships"][0]
		place_nodes(rel["startNode"], rel["endNode"])

	res_row = not_neighbors()

	for tpl in res_row:
		print node_hash[tpl[0]] + " is " + node_hash[tpl[1]]


		

context =  raw_input("Context (common): ")
if (context == ""):
	context = "common"

text = ""
while (text == ""):
	text =  raw_input("Phrase: ")

phrase_type = "q" if text[len(text)-1] == "?" else "a"

result = loads(server.parse(text))

if (context == "ignore"):
	print json.dumps(result)
	find_implicit_relations()
else:
	# !! Performs only for one sentence
	# save phrase dependencies to db
	sentence = result["sentences"][0]
	# save dependencies
	save_dependencies(sentence["dependencies"])
	# check class relations
	check_class_relations(sentence["dependencies"])
	check_lemmas(sentence["words"])

	find_implicit_relations()



