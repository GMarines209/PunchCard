from flask import Flask, jsonify, request
from flask import render_template
import cache

app = Flask(__name__)
active_fighter = None

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/live") 
def live_results():
    return

@app.route("/upcomming")
def upcomming():
    return

@app.route("/current")
def current():
    return jsonify({"active_fighter_id": active_fighter})

@app.route("/fighter") # combined with set_acive so it returns stats and sets current
def fighter_stats():
    global active_fighter
    fighter_id = request.args.get("id")
    
    if not fighter_id:
        return jsonify({"error": "Missing 'id' parameter"}), 400
    
    full_stats = cache.get_stats(fighter_id)
    if not full_stats:
        return jsonify({"error": "Fighter not found"}), 404
    
    active_fighter = fighter_id
    
    # return jsonify({"success": True, "now_displaying": active_fighter}) 
    return jsonify(full_stats)

@app.route("/fighters")
def fighters_list():
    fighter_name = request.args.get("name")
    if not fighter_name:
        return jsonify({"error": "Missing 'name' parameter"}), 400
    names = cache.handle_search(fighter_name)
    if names is None:
        return jsonify({"error": "No fighter URL found"}), 404

    return jsonify(names)
