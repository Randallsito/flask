from flask import Flask, jsonify, render_template_string
import subprocess
import json

app = Flask(__name__)

SCRIPTS_DIR = "/var/www/scripting/scripts"
SERVER_IP = "127.0.0.1"

SERVICES = {
    "Web Apache": "apache2",
    "Mail Postfix": "postfix",
    "DNS Bind9": "named",
    "IMAP Dovecot": "dovecot",
    "FTP vsftpd": "vsftpd"
}

WEBS = {
    "Webmail": "https://mail.group07.smx2.internal/",
    "WordPress": "https://wordpress.group07.smx2.internal/",
    "Tickets": "https://tickets.group07.smx2.internal/",
    "Wiki": "https://wiki.group07.smx2.internal/",
    "phpMyAdmin": "https://phpmyadmin.group07.smx2.internal/"
}

HTML = """
<!DOCTYPE html>
<html lang="ca">
<head>
<meta charset="UTF-8">
<title>Monitorització del servidor</title>

<style>
* { box-sizing: border-box; }

body {
    font-family: Arial, sans-serif;
    background: #f3f4f6;
    margin: 0;
    color: #111827;
}

header {
    background: #1f2937;
    color: white;
    padding: 16px;
    text-align: center;
}

header h1 {
    margin: 0;
    font-size: 28px;
}

header p {
    margin: 6px 0 0 0;
    font-size: 14px;
}

.container {
    width: 96%;
    max-width: 1450px;
    margin: 20px auto;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
}

.card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.10);
    overflow-wrap: break-word;
    word-break: break-word;
}

.card h2 {
    margin-top: 0;
    font-size: 21px;
}

.ok {
    color: green;
    font-weight: bold;
}

.error {
    color: red;
    font-weight: bold;
}

.small {
    font-size: 14px;
}

.bar {
    background: #ddd;
    border-radius: 12px;
    overflow: hidden;
    height: 24px;
}

.bar-fill {
    background: #2563eb;
    color: white;
    height: 24px;
    text-align: center;
    line-height: 24px;
    font-weight: bold;
    min-width: 45px;
}

.links a {
    display: inline-block;
    margin: 5px;
    padding: 9px 13px;
    background: #2563eb;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-size: 14px;
}

.links a:hover {
    background: #1d4ed8;
}

.full {
    grid-column: 1 / -1;
}

.table-wrap {
    width: 100%;
    overflow-x: auto;
}

.web-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.web-table th,
.web-table td {
    padding: 9px;
    border-bottom: 1px solid #e5e7eb;
    text-align: left;
}

.web-table th {
    background: #f9fafb;
}

footer {
    text-align: center;
    margin: 22px;
    color: #6b7280;
    font-size: 14px;
}
</style>
</head>

<body>

<header>
    <h1>Panell de Monitorització</h1>
    <p>Servidor group07 - Flask + Gunicorn</p>
</header>

<div class="container">
    <div class="cards">

        <div class="card">
            <h2>Estat API</h2>
            <p class="ok">Funcionant correctament</p>
        </div>

        <div class="card">
            <h2>Disc</h2>
            <p><b>Sistema:</b><br>{{ disk.filesystem }}</p>
            <p><b>Mida:</b> {{ disk.size }}</p>
            <p><b>Usat:</b> {{ disk.used }}</p>
            <p><b>Lliure:</b> {{ disk.available }}</p>
            <div class="bar">
                <div class="bar-fill" style="width: {{ disk.use_percent }};">
                    {{ disk.use_percent }}
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Base de dades</h2>
            {% if db.status == "ok" %}
                <p class="ok">MySQL connectat correctament</p>
            {% else %}
                <p class="error">Error MySQL</p>
            {% endif %}
        </div>

        <div class="card">
            <h2>Serveis</h2>
            {% for name, info in services.items() %}
                <p class="small">
                    <b>{{ name }}</b>:
                    {% if info.status == "active" %}
                        <span class="ok">actiu</span>
                    {% else %}
                        <span class="error">{{ info.status }}</span>
                    {% endif %}
                </p>
            {% endfor %}
        </div>

        <div class="card">
            <h2>Usuaris</h2>
            <p><b>Total:</b> {{ users|length }}</p>
            <p class="small">{{ users[:12]|join(", ") }}...</p>
        </div>

        <div class="card">
            <h2>JSON</h2>
            <div class="links">
                <a href="/api/disk" target="_blank">Disc</a>
                <a href="/api/users" target="_blank">Usuaris</a>
                <a href="/api/db" target="_blank">DB</a>
                <a href="/api/services" target="_blank">Serveis</a>
                <a href="/api/webs" target="_blank">Webs</a>
            </div>
        </div>

        <div class="card full">
            <h2>Estat de webs HTTPS</h2>
            <div class="table-wrap">
                <table class="web-table">
                    <tr>
                        <th>Web</th>
                        <th>URL</th>
                        <th>Codi HTTP</th>
                        <th>Estat</th>
                    </tr>
                    {% for name, info in webs.items() %}
                    <tr>
                        <td><b>{{ name }}</b></td>
                        <td>{{ info.url }}</td>
                        <td>{{ info.code }}</td>
                        <td>
                            {% if info.code == 200 %}
                                <span class="ok">OK</span>
                            {% else %}
                                <span class="error">ERROR</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

    </div>
</div>

<footer>
    Aplicació de monitorització creada amb Flask, Bash, Python i Gunicorn
</footer>

</body>
</html>
"""

def run_json(command):
    result = subprocess.check_output(command)
    return json.loads(result.decode())

def get_services():
    data = {}

    for visible_name, systemd_name in SERVICES.items():
        status = subprocess.run(
            ["systemctl", "is-active", systemd_name],
            capture_output=True,
            text=True
        ).stdout.strip()

        data[visible_name] = {
            "service": systemd_name,
            "status": status
        }

    return data

def get_webs():
    data = {}

    for name, url in WEBS.items():
        host = url.replace("https://", "").replace("/", "")

        try:
            result = subprocess.run(
                [
                    "curl",
                    "-k",
                    "-L",
                    "-s",
                    "-o", "/dev/null",
                    "-w", "%{http_code}",
                    "--connect-timeout", "4",
                    "--max-time", "6",
                    "--resolve", f"{host}:443:{SERVER_IP}",
                    url
                ],
                capture_output=True,
                text=True
            )

            output = result.stdout.strip()

            if output.isdigit():
                code = int(output)
            else:
                code = 0

        except Exception:
            code = 0

        data[name] = {
            "url": url,
            "code": code
        }

    return data

@app.route("/")
def index():
    disk = run_json([f"{SCRIPTS_DIR}/check_disk.sh"])
    users = run_json([f"{SCRIPTS_DIR}/list_users.sh"])
    db = run_json([f"{SCRIPTS_DIR}/db_check.py"])
    services = get_services()
    webs = get_webs()

    return render_template_string(
        HTML,
        disk=disk,
        users=users,
        db=db,
        services=services,
        webs=webs
    )

@app.route("/api/disk")
def api_disk():
    return jsonify(run_json([f"{SCRIPTS_DIR}/check_disk.sh"]))

@app.route("/api/users")
def api_users():
    return jsonify(run_json([f"{SCRIPTS_DIR}/list_users.sh"]))

@app.route("/api/db")
def api_db():
    return jsonify(run_json([f"{SCRIPTS_DIR}/db_check.py"]))

@app.route("/api/services")
def api_services():
    return jsonify(get_services())

@app.route("/api/webs")
def api_webs():
    return jsonify(get_webs())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)