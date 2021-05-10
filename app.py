from flask import Flask, request, send_file, json
from flask_cors import CORS

from service import *

app = Flask(__name__)
CORS(app)


@app.route('/test', methods=['POST'])
def test():
    a = {"1": "a", "2": ["a", "b", "啊啊"]}
    return json.dumps(a, ensure_ascii=False)


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


@app.route('/search_graph', methods=['POST'])
def search_graph():
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
        the_graph = nodes_to_graphs(id_list)

        res['data'] = the_graph
        res['code'] = 200
        res['msg'] = "success"
    except Exception as e:
        res['msg'] = e

    return res


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
