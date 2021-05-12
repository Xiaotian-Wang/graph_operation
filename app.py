from flask import Flask, request, send_file, json
from flask_cors import CORS

from service import *

app = Flask(__name__)
CORS(app)

'''
@app.route('/search_nodes', methods=['POST'])
def search_nodes():
    res = {
        "code": 400,
        "data": {},
        "msg": "failure"
    }
    try:
        the_request = request.form
        the_request = dict(the_request)
        keyword = the_request['keyword']
        search_result = search(keyword, mode="contain")
        the_graph = show_graph(np.array([search_result]))

        res['data'] = the_graph
        res['code'] = 200
        res['msg'] = "success"
    except Exception as e:
        res['msg'] = e

    return res
'''

@app.route('/init', methods=['POST'])
def init():
    data = request.json
    print(data)
    print(type(data))
    return "type(data)"

@app.route('/search_graph_slow', methods=['POST'])
def search_graph_slow():
    """
    按照标准ID搜索图（慢速）。

    因为该方法需要做任何两点之间的遍历，所以当节点较多时，运行速度较慢。时间复杂度为O(N^2），N为标准节点以及其1跳节点的数量

    输入：
        request.POST的form格式，KEY: 'keyword', VALUE: 字符串，其值为:标准的ID，可以是多个，用英文的逗号','隔开，逗号后不加空格。

    返回：
        所有ID对应的标准的一跳图，以及所有节点间的直接关系。例如， 标准1的一跳节点与标准2的一跳节点之间若有关系，则该关系也会被返回。

    """
    res = {
        "code": 400,
        "data": {},
        "msg": "failure"
    }
    try:
        the_request = request.json
        the_request = dict(the_request)
        keyword = the_request['keyword']
        search_result = search(keyword, mode="contain")
        id_list = get_id_list(search_result)
        id_list_copy = list(id_list)
        for item in id_list:
            one_jump = one_jump_graph(item).to_ndarray(dtype='object')
            one_jump = show_graph(one_jump)
            for item1 in one_jump['nodes']:
                id_list_copy.append(item1['id'])

        the_graph = nodes_to_graphs(id_list_copy)

        res['data'] = the_graph
        res['code'] = 200
        res['msg'] = "success"
    except Exception as e:
        res['msg'] = e

    return res


@app.route('/search_graph_fast', methods=['POST'])
def search_graph_fast():
    """
    按照标准ID搜索图（快速）。

    该方法不需要做一跳节点间的任何两点遍历，只需要做标准节点间的任何两点遍历。所以当一跳节点较多时，运行时间线性增加。
    时间复杂度为O(NM^2），N为标准节点以及其1跳节点的数量, M为标准节点的数量。但是由于M的数量取决于搜索的标准数量，通常在5个以内，
    所以此处可按常量处理，因此时间复杂度为O(N)

    输入：
        request.POST的form格式，KEY: 'keyword', VALUE: 字符串，其值为:标准的ID，可以是多个，用英文的逗号','隔开，逗号后不加空格。
    返回：
        所有ID对应的标准的一跳图，以及标准节点间的直接关系。注意，标准1的一跳节点与标准2的一跳节点之间若有关系，则该关系可能不会被返回。

    """
    res = {
        "code": 400,
        "data": {},
        "msg": "failure"
    }
    try:
        the_request = request.json
        the_request = dict(the_request)
        keyword = the_request['keyword']
        search_result = search(keyword, mode="contain")
        id_list = get_id_list(search_result)
        original_graph = nodes_to_graphs(id_list)
        for item in id_list:
            one_jump = one_jump_graph(item).to_ndarray(dtype='object')
            one_jump = show_graph(one_jump)
            original_graph['nodes'] += one_jump['nodes']
            original_graph['edges'] += one_jump['edges']

        the_graph = {}
        the_graph['nodes'] = unique(original_graph['nodes'])
        the_graph['edges'] = unique(original_graph['edges'])
        res['data'] = the_graph
        res['code'] = 200
        res['msg'] = "success"
    except Exception as e:
        res['msg'] = e

    return res


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
