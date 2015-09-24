from neo4jrestclient.client import GraphDatabase
gdb = GraphDatabase("http://localhost:7474/db/data/", username="neo4j", password="123")
import json

def build_query(nodes_num):
    if (nodes_num < 3):
        raise Exception("Number of nodes cannot be less than 3")

    q = "MATCH "
    returns = []
    for i in range(1, nodes_num + 1):
        node_name = "n" + str(i)
        returns.append(node_name)

        if i == nodes_num:
            add = "(%s)" % node_name
        else:
            rel_name = "r" + str(i)
            returns.append(rel_name)
            add = "(%s)-[%s:class]-" % (node_name, rel_name)
        q += add

    return q + " return " + ",".join(returns)



# Responsible for right order: firstly child, then parent, according to db relations
def place_nodes(child, parent, places):
        try:
            # is a child in a list?
            ch_i = places.index(child)
            try:
                # is a parent in a list
                par_i = places.index(parent)
                places.insert(par_i, child)
                return places
            except:
                # no parent, but there is a child
                places.insert(ch_i + 1, parent)
                return places
        except:
            try:
                # no child, is a parent?
                par_i = places.index(parent)
                places.insert(par_i, child)
                return places
            except:
                # nothing, adding both
                places.append(child)
                ch_i = places.index(child)
                places.insert(ch_i + 1, parent)
                return places


def sort_nodes(graph):
    nodes = {}
    chain = []
    for node in graph["nodes"]:
        nodes[node["id"]] = node["labels"][0]

    for rel in graph["relationships"]:
        before_id = rel["startNode"]
        after_id = rel["endNode"]

        chain = place_nodes(before_id, after_id, chain)

    def get_values(id):
        return nodes[id]

    return map(get_values, chain)


# Recursively increases number of intermediate nodes until None result
def get_possible_chains(nodes_num, chains=[]):
    q = build_query(nodes_num)
    res = gdb.query(q = q, data_contents=True)
    try:
        chain = sort_nodes(res.graph[0])
        # here nodes are already list of strings
        chains.append(chain)
        return get_possible_chains(nodes_num + 1, chains)
    except:
        return chains


def find_implicit_relations():
    places = []

    # Number of nodes to select o - [:class] - o - [:class] - o
    # First implicit relation is between 1 and 3 nodes
    nodes = 3
    chains = get_possible_chains(nodes)
    print chains