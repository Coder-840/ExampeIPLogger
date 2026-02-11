from flask import Flask, request, render_template_string, session, redirect, url_for
import datetime
import os

app = Flask(__name__)
app.secret_key = "aby2837aufwh228dewuey389" # Needed for login sessions

# --- CONFIGURATION ---
ADMIN_PASSWORD = "your-secret-password"  # CHANGE THIS!
recorded_ips = []

# --- HTML TEMPLATES ---

HOME_HTML = """
<!DOCTYPE html>
<html>
<head><title>CAUGHT</title><style>
    body, html { height: 100%; margin: 0; display: flex; justify-content: center; align-items: center; background: #000; color: red; font-family: 'Arial Black', sans-serif; overflow: hidden; }
    h1 { font-size: 6vw; text-align: center; text-transform: uppercase; animation: blinker 0.8s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
</style></head>
<body><h1>YOUR IP HAS BEEN RECORDED LOL</h1></body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body style="font-family: sans-serif; text-align: center; padding-top: 100px;">
    <h2>Enter Admin Password</h2>
    <form method="POST">
        <input type="password" name="password" required>
        <button type="submit">Login</button>
    </form>
    {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>Admin Dashboard</title><style>
    body { font-family: sans-serif; padding: 30px; background: #f4f4f4; }
    table { width: 100%; border-collapse: collapse; background: white; margin-top: 20px; }
    th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
    th { background: #333; color: white; }
    .btn-clear { background: red; color: white; padding: 10px 20px; border: none; cursor: pointer; border-radius: 5px; }
</style></head>
<body>
    <div style="display: flex; justify-content: space-between;">
        <h1>Recorded IPs</h1>
        <form action="/clear" method="POST">
            <button class="btn-clear" onclick="return confirm('Clear everything?')">CLEAR ALL LOGS</button>
        </form>
    </div>
    <table>
        <tr><th>Timestamp</th><th>IP Address</th><th>User Agent</th></tr>
        {% for entry in logs %}
        <tr><td>{{ entry.time }}</td><td><code>{{ entry.ip }}</code></td><td><small>{{ entry.ua }}</small></td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def log_ip():
    ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recorded_ips.append({"time": timestamp, "ip": ip_addr, "ua": user_agent})
    return render_template_string(HOME_HTML)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Handle Login
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return render_template_string(LOGIN_HTML, error="Wrong Password!")

    # Check if logged in
    if not session.get('logged_in'):
        return render_template_string(LOGIN_HTML)

    return render_template_string(DASHBOARD_HTML, logs=recorded_ips[::-1])

@app.route('/clear', methods=['POST'])
def clear_logs():
    if session.get('logged_in'):
        recorded_ips.clear()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
