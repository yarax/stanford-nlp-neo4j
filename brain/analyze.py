from neo4jrestclient.client import GraphDatabase
gdb = GraphDatabase("http://localhost:7474/db/data/", username="neo4j", password="123")

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