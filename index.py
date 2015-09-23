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
from nltk.stem.wordnet import WordNetLemmatizer
from brain import nlp
from brain import analyze

from stanford_corenlp_python import jsonrpc
from simplejson import loads
server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(), jsonrpc.TransportTcpIp(addr=("127.0.0.1", 3456)))

context =  raw_input("Context (common): ")
if (context == ""):
	context = "common"

text = ""
text =  raw_input("Phrase: ")
if text != "":
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
		nlp.save_dependencies(sentence["dependencies"], context)
		# check class relations
		nlp.check_class_relations(sentence["dependencies"])
		nlp.check_lemmas(sentence["words"])

		analyze.find_implicit_relations()



