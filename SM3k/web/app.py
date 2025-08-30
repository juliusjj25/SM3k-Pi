from flask import Flask, jsonify
import time

app = Flask(__name__)

# globals filled by main
LATEST = {"ts": time.time(), "status":{}}

@app.route("/status")
def status():
    return jsonify(LATEST)

def update_status(data: dict):
    """Called from main loop with most recent readings/control state"""
    LATEST["ts"] = time.time()
    LATEST["status"] = data
