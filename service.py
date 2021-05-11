from py2neo import Graph, Node, Path, Relationship
from py2neo.matching import *
import numpy as np

NEO4J_HOST = 'http://10.216.6.221:7474/'
NEO4J_USER_NAME = 'neo4j'
NEO4J_PASSWORD = '12345678aA'

graph = Graph(NEO4J_HOST, username=NEO4J_USER_NAME, password=NEO4J_PASSWORD)


def unique(data: list):
    """
    对于输入的列表，返回一个去重的列表。区别于set函数，主要针对unhashable的数据类型
    """
    temp = []
    for item in data:
        if item not in temp:
            temp.append(item)
    return temp


def search(keyword: str, mode='contain'):
    """
    按照结点名称查找图中的结点，返回结点的列表，其元素为Node格式。函数有2种模式"exact"精确模式和"contain"包含模式（默认）。
    """
    if keyword.replace(" ", "") == "":
        return []

    if mode == "exact":
        # graph.run("match (n) where n.name = ")
        nodes = NodeMatcher(graph)
        node = nodes.match(name=keyword).all()
        return node
    elif mode == "contain":
        # 搜索文本可以用","分隔开，以实现多关键词搜索，搜索条件为只需包含一个分隔开的关键词
        keyword = keyword.split(",")
        nodes = NodeMatcher(graph)
        node = []
        for item in keyword:
            node.append(nodes.match(name=CONTAINS(item), type='标准').order_by("size(_.name)").all())
        final_node = node[0]
        for item in node:
            final_node = set(final_node).union(set(item))
        if len(final_node) > 100:
            final_node = list(final_node)[0:100]
        return final_node


def show_graph(res):
    """
    此函数的输入为py2neo语句graph.run("SOME CYPHER QUERY").to_ndarray(dtype = object)的结果，
    其中CYPHER语句返回的内容应该是结点和边，即类型为"Node"或"Relation", 此函数的返回数据为data字典，
    格式为所要求graph的结点与边分离的数据格式.
    """

    data = {"nodes": [],
            "edges": []}
    for res in res:
        for item in res:
            if str(type(item)) == "<class 'py2neo.data.Node'>":
                node = {'id': str(item.identity), 'name': item['name'], 'type': item['type']}
                node['std_no'] = ""
                node['std_name'] = ""
                if node['type'] == "标准":
                    the_name = node['name'].split('##')
                    if len(the_name) == 2:
                        node['std_no'] = the_name[0]
                        node['std_name'] = the_name[1]
                    elif len(the_name) == 1:
                        node['std_no'] = the_name[0]
                data["nodes"].append(node)
            elif str(type(item)) == "<class 'py2neo.data.Relation'>":
                edge = {'source': str(item.start_node.identity), 'target': str(item.end_node.identity), 'relation': item['name']}
                data["edges"].append(edge)
    data['nodes'] = unique(data['nodes'])
    data['edges'] = unique(data['edges'])
    return data


def one_jump_graph(name):
    """
    输入一个结点的id, 返回以这个结点为中心的一跳图，返回数据类型是'py2neo.database.work.Cursor'.
    如果需要 np.ndarray 类型, 可以使用 '.to_ndarray(dtype = object)' 命令
    """
    if type(name) != str:
        name = str(name)

    cypher_command = "match (a)-[b]-(c) where id(a) = " + name + " return a,b,c"
    res = graph.run(cypher_command)
    return res


def get_id_list(nodes: list):
    """
    输入节点的列表(list of Nodes), 返回列表中节点的id的列表
    """
    id_list = []
    for item in nodes:
        id_list.append(item.identity)
    return id_list


def nodes_to_graphs(nodes=None, jumps=0):
    """
    通过节点ID列表，搜索节点和节点间的关系（直接、1跳或2跳），返回构成的图。

    注意，此方法需要多次的两两节点间遍历，时间复杂度为O(N^2），N为节点数量，因此在节点数量较多时候，运行较慢。
    建议节点数在50及以下时使用。

    :param nodes: 节点ID的列表
    :param jumps: 跳数， 0表示只包含直接关系（0跳），1代表0跳和1跳，2代表0跳、1跳和2跳
    :return: 节点和其中的关系（直接或间接）构成的图

    """

    if nodes is None:
        nodes = ["1994", "1962", "1595"]
    for i in range(len(nodes)):
        nodes[i] = str(nodes[i])

    result = []
    for i in range(len(nodes) - 1):
        for j in range(i + 1, len(nodes)):
            res = graph.run(
                r"MATCH (a)-[b]-(c) where id(a) = " + nodes[i] + " and id(c) = " + nodes[j] + " return a,b,c")
            res = res.to_ndarray(dtype=object)
            if len(res) > 0:
                result.append(res)
    if jumps >= 1:
        for i in range(len(nodes) - 1):
            for j in range(i + 1, len(nodes)):
                res = graph.run(r"MATCH (a)-[b]-(c)-[d]-(e) where id(a) = " + nodes[i] + " and id(e) = " + nodes[
                    j] + " return a,b,c,d,e")
                res = res.to_ndarray(dtype=object)
                if len(res) > 0:
                    result.append(res)
    if jumps >= 2:
        for i in range(len(nodes) - 1):
            for j in range(i + 1, len(nodes)):
                res = graph.run(
                    r"MATCH (a)-[b]-(c)-[d]-(e)-[f]-(g) where id(a) = " + nodes[i] + " and id(g) = " + nodes[
                        j] + " return a,b,c,d,e,f,g")
                res = res.to_ndarray(dtype=object)
                if len(res) > 0:
                    result.append(res)

    nodes_int = list(map(int, nodes))
    original_nodes = graph.nodes.get(nodes_int)

    graph1 = {'nodes': [],
              'edges': []}
    for item in result:
        temp = show_graph(item)
        graph1['nodes'] += temp['nodes']
        graph1['edges'] += temp['edges']

    original_graph = show_graph([original_nodes])
    graph1['nodes'] += original_graph['nodes']
    graph1['edges'] += original_graph['edges']

    graph1['nodes'] = unique(graph1['nodes'])
    graph1['edges'] = unique(graph1['edges'])

    return graph1
