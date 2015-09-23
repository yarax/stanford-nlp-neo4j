import time
from neo4jrestclient.client import GraphDatabase
from nltk.stem.wordnet import WordNetLemmatizer

RELATION_TYPES = {
	"class" : "class"
}

gdb = GraphDatabase("http://localhost:7474/db/data/", username="neo4j", password="123")

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


def save_dependencies(dependencies, context):
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


def prepare_words_for_db(sentence):
	def process(w):
		w = w.replace("-", "_")
		w = w.replace("/", "_")
		return w
		

	for i, word in enumerate(sentence["dependencies"]):
		sentence["dependencies"][i][1] = process(sentence["dependencies"][i][1])
		sentence["dependencies"][i][2] = process(sentence["dependencies"][i][2])

	for i, word in enumerate(sentence["words"]):
		sentence["words"][i][0] = process(sentence["words"][i][0])
		sentence["words"][i][1]['Lemma'] = process(sentence["words"][i][1]['Lemma'])

	return sentence


