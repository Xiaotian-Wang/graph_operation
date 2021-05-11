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


@app.route('/search_graph_slow', methods=['POST'])
def search_graph_slow():
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
