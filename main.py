from flask import Flask, request, render_template_string
import datetime
import os

app = Flask(__name__)

# In-memory storage (Note: This clears if Railway restarts the app)
recorded_ips = []

# --- HTML TEMPLATES ---

# The "Trap" Page
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>CAUGHT</title>
    <style>
        body, html {
            height: 100%;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #000;
            color: #ff0000;
            font-family: 'Arial Black', sans-serif;
            overflow: hidden;
        }
        h1 {
            font-size: 6vw;
            text-align: center;
            text-transform: uppercase;
            text-shadow: 5px 5px #550000;
            animation: blinker 0.8s linear infinite;
        }
        @keyframes blinker {
            50% { opacity: 0; }
        }
    </style>
</head>
<body>
    <h1>YOUR IP HAS BEEN RECORDED LOL</h1>
</body>
</html>
"""

# The Dashboard Page
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>IP Logger Admin</title>
    <style>
        body { font-family: sans-serif; padding: 30px; background: #f4f4f4; }
        table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #333; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .header { display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Recorded IP Addresses</h1>
        <p>Total Hits: {{ logs|length }}</p>
    </div>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>IP Address</th>
            <th>User Agent (Device Info)</th>
        </tr>
        {% for entry in logs %}
        <tr>
            <td>{{ entry.time }}</td>
            <td><code>{{ entry.ip }}</code></td>
            <td><small>{{ entry.ua }}</small></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def log_ip():
    # Railway/Proxies pass the real IP through X-Forwarded-For
    ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
    # If multiple IPs are in header, grab the first one
    if ',' in ip_addr:
        ip_addr = ip_addr.split(',')[0]
        
    user_agent = request.headers.get('User-Agent')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to our list
    recorded_ips.append({
        "time": timestamp,
        "ip": ip_addr,
        "ua": user_agent
    })
    
    # Print to Railway console logs for backup
    print(f"NEW HIT: {ip_addr} at {timestamp}")
    
    return render_template_string(HOME_HTML)

@app.route('/dashboard')
def dashboard():
    # Show the logs (reversed so newest are at the top)
    return render_template_string(DASHBOARD_HTML, logs=recorded_ips[::-1])

if __name__ == "__main__":
    # Railway sets the PORT environment variable automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
