from flask import Flask, request, render_template_string
import datetime
import os

app = Flask(__name__)

# List to store logs in memory
recorded_ips = []

# Simple HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>IP Logger Dashboard</title></head>
<body style="font-family: sans-serif; padding: 20px;">
    <h1>Logged Visits</h1>
    <table border="1" cellpadding="10" style="width:100%; border-collapse: collapse;">
        <tr style="background: #eee;">
            <th>Timestamp</th>
            <th>IP Address</th>
            <th>Device/User-Agent</th>
        </tr>
        {% for entry in logs %}
        <tr>
            <td>{{ entry.time }}</td>
            <td>{{ entry.ip }}</td>
            <td>{{ entry.ua }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def log_ip():
    ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to the list
    recorded_ips.append({
        "time": timestamp,
        "ip": ip_addr,
        "ua": user_agent
    })
    
    return "<h1>Hello!</h1>"

@app.route('/dashboard')
def dashboard():
    # Pass the list of logs to the template
    return render_template_string(DASHBOARD_HTML, logs=recorded_ips[::-1]) # Show newest first

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
