from flask import Flask, jsonify

from unity.unity_server import UnityServer
from core.utils.environment import Environment


app = Flask(__name__)
unity_server = UnityServer()


@app.route('/get_action', methods=['GET'])
def get_action():
    action, manager_state = unity_server.get_next_action()
    action = list(map(lambda x: x.value, action))
    outside_calls = list(map(lambda x: int(x), manager_state.outside_calls))
    elevators_state = list(map(lambda x: x.going_to_level, manager_state.elevators_state))
    passengers_weight = list(map(lambda x: x.current_weight, manager_state.elevators_state))
    max_weight = list(map(lambda x: x.max_weight, manager_state.elevators_state))
    is_door_open = list(map(lambda x: int(x.is_open_door), manager_state.elevators_state))
    return jsonify({
        "action": action,
        "outside_calls": outside_calls,
        "elevators_state": elevators_state,
        "passengers_weight": passengers_weight,
        "max_weight": max_weight,
        "is_door_open": is_door_open
    })


@app.route('/get_settings', methods=['GET'])
def get_settings():
    return jsonify({"elevators": Environment.ELEVATORS, "levels": Environment.LEVELS})


if __name__ == '__main__':
    app.run(port=Environment.UNITY_SERVER_PORT)
