from flask import Flask, request, jsonify
from optimizer import optimise_team, load_data
import os

app = Flask(__name__)

@app.route("/build-team", methods=["POST"])
def build_team():
    """
    Expects JSON like:
      {
        "starters": ["Pikachu"],
        "hp_floor": 80,
        "atk_floor": 100,
        "def_floor": 0,
        "spatk_floor": 0,
        "spdef_floor": 0,
        "spd_floor": 0
      }
    """
    payload = request.get_json() or {}
    team = optimise_team(**payload).to_dict(orient="records")
    return jsonify(team), 200

@app.route("/health", methods=["GET"])
def health():
    return "ok", 200

if __name__ == "__main__":
    # local test: python api.py
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
