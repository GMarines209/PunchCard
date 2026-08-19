from flask import Flask, jsonify, request
from flask import render_template
import cache, database, utils, render, live
from flask import send_from_directory, abort
import glob,os

app = Flask(__name__)
active_fighter = None

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/live") 
def live_results():
    l = live.live()
    return jsonify(l)

@app.route("/upcoming")
def upcoming():
    event_id = live.get_upcomming()
    return jsonify(event_id)

@app.route("/current")
def current():
    return jsonify({"active_fighter_id": active_fighter})

@app.route("/display")
def display_fighter():
    global active_fighter
    fighter_id = request.args.get("id")
    mode = request.args.get("mode")

    if not fighter_id:
        return jsonify({"error": "Missing 'id' parameter"}), 400

    full_stats = cache.get_stats(fighter_id)
    if not full_stats:
        return jsonify({"error": "Fighter not found"}), 404

    active_fighter = fighter_id
    return jsonify({"success": True, "name": full_stats.get("name", "fighter")})

@app.route("/render")
def render_fighter():
    fighter_id = request.args.get("id") or active_fighter
    stat_type = request.args.get("type")
    pi = request.args.get("view") == "pi"

    if not fighter_id:
        return jsonify({"error": "No fighter selected"}), 404
    
    full_stats = cache.get_stats(fighter_id)

    full_stats["weightclass"] = utils.normalize_weight(full_stats["weight"])
    full_stats["age"] = utils.normalize_age(full_stats["dob"])
    full_stats["height"] = utils.normalize_height(full_stats["height"])

    return render_template("fighter_showcase.html", fighter=full_stats, stat_page=stat_type, pi=pi)

@app.route("/serve")
def serve_render():
    fighter_id = request.args.get("id")
    stat_page = request.args.get("page", "physical")
    if not fighter_id:
        return jsonify({"error": "Missing 'id' parameter"}), 400
    render.main(fighter_id)
    matches = glob.glob(f"renders/{fighter_id}_{stat_page}_*.png")
    if not matches:
        return jsonify({"error": "Render failed"}), 500
    return send_from_directory("renders", os.path.basename(max(matches)))

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
    names = database.search_fighters(fighter_name)

    return jsonify(names)

@app.route("/fighters/deep")
def deep_search():
    fighter_name = request.args.get("name")
    if not fighter_name:
        return jsonify({"error": "Missing 'name' parameter"}), 400
    names = cache.handle_deep_search(fighter_name)
    return jsonify(names) 

@app.route("/images/<fighterid>")
def serve_image(fighterid):
    fid = fighterid.removesuffix(".png")
    if(fid == "default"):
        return send_from_directory("images", f"{fid}.png")
    try:
        int(fid, 16)
    except ValueError:
        abort(404)
    if len(fid) != 16:
        abort(404)
    return send_from_directory("images", f"{fid}.png")