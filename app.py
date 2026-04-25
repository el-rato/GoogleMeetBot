from flask import Flask, render_template, request, jsonify,send_from_directory
from http import HTTPStatus
import threading
import time
from googlemeetjoiningbot import join_meet

app = Flask(__name__)

# Global state
bot_thread = None
cancel_event = threading.Event()
bot_logs = []
bot_status = "Offline"  # Offline, Running, Stopped

def add_log(msg):
    timestamp = time.strftime('%H:%M:%S')
    bot_logs.append(f"[{timestamp}] {msg}")
    print(f"[BOT] {msg}")

def run_bot_worker(meet_link, duration, profile):
    global bot_status
    bot_status = "Running"
    add_log(f"Initializing bot for link: {meet_link} ...")
    try:
        join_meet(meet_link, duration, profile, add_log, cancel_event)
    except Exception as e:
        add_log(f"CRITICAL ERROR: {str(e)}")
    
    bot_status = "Offline"
    if cancel_event.is_set():
        add_log("Bot was successfully stopped.")
    else:
        add_log("Bot run completed.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'status': bot_status,
        'logs': bot_logs[-50:]  # Return last 50 logs
    })

@app.route('/api/start', methods=['POST'])
def start_bot():
    global bot_thread, cancel_event, bot_logs, bot_status
    if bot_status == "Running":
        return jsonify({"error": "Bot is already running"}), 400
    
    data = request.json
    meet_link = data.get('link', '')
    duration = float(data.get('duration', 90))
    profile = data.get('profile', 'Profile 2')
    
    if not meet_link:
        return jsonify({"error": "Meet link is required"}), 400

    bot_logs.clear()
    cancel_event.clear()
    
    bot_thread = threading.Thread(target=run_bot_worker, args=(meet_link, duration, profile))
    bot_thread.start()
    
    return jsonify({"message": "Bot started successfully"}), 200

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    global bot_status
    if bot_status != "Running":
        return jsonify({"error": "Bot is not running"}), 400
    
    add_log("Sending stop signal to bot... Please wait.")
    cancel_event.set()
    bot_status = "Stopping..."
    return jsonify({"message": "Stop signal sent"}), 200

@app.route("/home")
def home():
    return "LAUDA"
@app.route("/api/lauda", methods=['GET','POST'])
def anotherlawda():
    return send_from_directory("C:\\Users\\USER\\OneDrive\\Desktop\\MeetBot\\static", "cock.jpg")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5000)
