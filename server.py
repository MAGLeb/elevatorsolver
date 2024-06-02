from flask import Flask, jsonify

from unity.unity_server import UnityServer
from core.utils.environment import Environment
from utils.utils import initialise_settings_wandb

# SETTINGS WANDB
initialise_settings_wandb(["prediction"])

app = Flask(__name__)
unity_server = UnityServer()


@app.route('/get_action', methods=['GET'])
def get_action():
    action, manager_state = unity_server.get_next_action()
    action = list(map(lambda x: x.value, action))
    outside_calls = list(map(lambda x: int(x.value), manager_state.outside_calls))
    elevators_state = list(map(lambda x: x.going_to_level, manager_state.elevators_state))
    return jsonify({"action": action, "outside_calls": outside_calls, "elevators_state": elevators_state})


@app.route('/get_settings', methods=['GET'])
def get_settings():
    return jsonify({"elevators": Environment.ELEVATORS, "levels": Environment.LEVELS})


if __name__ == '__main__':
    app.run(port=Environment.UNITY_SERVER_PORT)
