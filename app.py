from flask import Flask, jsonify, render_template
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
            code = int(output) if output.isdigit() else 0

        except Exception:
            code = 0

        data[name] = {
            "url": url,
            "code": code
        }

    return data


@app.route("/")
def index():
    return render_template(
        "index.html",
        disk=run_json([f"{SCRIPTS_DIR}/check_disk.sh"]),
        users=run_json([f"{SCRIPTS_DIR}/list_users.sh"]),
        db=run_json([f"{SCRIPTS_DIR}/db_check.py"]),
        services=get_services(),
        webs=get_webs()
    )


@app.route("/llista")
def mostrar_llista():
    dades = ["apache2", "postfix", "named", "dovecot", "vsftpd"]

    return render_template(
        "list.html",
        nom_llista="Serveis del sistema",
        llista=dades
    )


@app.route("/api/disk")
def api_disk():
    return jsonify(run_json([f"{SCRIPTS_DIR}/check_disk.sh"])), 200


@app.route("/api/users")
def api_users():
    return jsonify(run_json([f"{SCRIPTS_DIR}/list_users.sh"])), 200


@app.route("/api/db")
def api_db():
    return jsonify(run_json([f"{SCRIPTS_DIR}/db_check.py"])), 200


@app.route("/api/services")
def api_services():
    return jsonify(get_services()), 200


@app.route("/api/webs")
def api_webs():
    return jsonify(get_webs()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)