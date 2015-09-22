from neo4jrestclient.client import GraphDatabase
gdb = GraphDatabase("http://localhost:7474/db/data/", username="neo4j", password="123")

# Context -> Classificator -> Information

qs = """MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r
MERGE (a:classificator)
MERGE (a:information)
MERGE (a:scope)
MERGE (a:common)
MATCH (a:classificator),(b:information) MERGE b-[rel:dobj]->a
MATCH (a:scope),(b:classificator) MERGE a-[rel:nsubj]->b
MATCH (a:common),(b:scope) MERGE a-[rel:nsubj]->b""";

row = qs.split("\n");
for q in row:
	print q
	gdb.query(q=q.strip())
