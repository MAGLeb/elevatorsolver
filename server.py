from flask import Flask, jsonify

from core.unity.unity_server import UnityServer
from core.utils.environment import Environment

app = Flask(__name__)
unity_server = UnityServer()


@app.route('/get_action', methods=['GET'])
def get_decision():
    action, outside_calls, inside_calls = unity_server.get_next_action()
    return jsonify({"action": action, "outside_calls": outside_calls, "inside_calls": inside_calls})


if __name__ == '__main__':
    app.run(port=Environment.UNITY_SERVER_PORT)
