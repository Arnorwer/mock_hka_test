from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from datetime import datetime
import os
import json
import threading

app = Flask(__name__)

# Tokens válidos fijos para pruebas
VALID_TOKEN_EMPRESA = "abcd1234"
VALID_TOKEN_PASSWORD = "abcd1234"

# Almacén en memoria de peticiones para el dashboard
LOGS = []
LOG_FILE = 'request_logs.json'
log_lock = threading.Lock()

# Cargar logs existentes al inicio
try:
    with log_lock:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                LOGS = json.load(f)
except (IOError, json.JSONDecodeError):
    LOGS = []

# ===========================
#  Dashboard HTML Template
# ===========================
DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Dashboard Mock HKA</title>
  <style>
    body { font-family: sans-serif; padding: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 1em; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f4f4f4; }
    tr:nth-child(even) { background: #fafafa; }
    pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; }
    .controls { margin-bottom: 1em; }
    .unauthorized { background-color: #ffe5e5; }
  </style>
</head>
<body>
  <h1>Dashboard Mock HKA</h1>
  <div class="controls">
    <form action="/clear-logs" method="post" style="display: inline;">
        <button type="submit">Clear Logs</button>
    </form>
  </div>
  <table>
    <thead>
      <tr>
        <th>#</th><th>Timestamp</th><th>Método</th><th>Endpoint</th><th>Datos</th><th>Respuesta</th>
      </tr>
    </thead>
    <tbody id="log-table-body">
      {% for entry in logs|reverse %}
      <tr class="{% if entry.response and entry.response.status == 401 %}unauthorized{% endif %}">
        <td>{{ loop.index }}</td>
        <td>{{ entry.time }}</td>
        <td>{{ entry.method }}</td>
        <td>{{ entry.path }}</td>
        <td><pre>{{ entry.data | tojson(indent=2) }}</pre></td>
        <td><pre>{{ entry.response | tojson(indent=2) }}</pre></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  <script>
    async function fetchLogs() {
      const res = await fetch('/api/logs');
      const logs = await res.json();
      const tbody = document.getElementById('log-table-body');
      tbody.innerHTML = '';
      logs.slice().reverse().forEach((entry, idx) => {
        const tr = document.createElement('tr');
        if (entry.response && entry.response.status == 401) {
            tr.classList.add('unauthorized');
        }
        const indexCell = document.createElement('td');
        indexCell.textContent = idx + 1;
        tr.appendChild(indexCell);
        ['time', 'method', 'path'].forEach(key => {
          const td = document.createElement('td');
          td.textContent = entry[key];
          tr.appendChild(td);
        });
        const dataTd = document.createElement('td');
        const preData = document.createElement('pre');
        preData.textContent = JSON.stringify(entry.data, null, 2);
        dataTd.appendChild(preData);
        tr.appendChild(dataTd);

        const respTd = document.createElement('td');
        const preResp = document.createElement('pre');
        preResp.textContent = JSON.stringify(entry.response, null, 2);
        respTd.appendChild(preResp);
        tr.appendChild(respTd);

        tbody.appendChild(tr);
      });
    }
    fetchLogs();
    setInterval(fetchLogs, 1000);
  </script>
</body>
</html>
"""

# ===========================
#  Helper: verificar token
# ===========================
def check_auth():
    token_empresa = request.headers.get('X-HKA-Token')
    token_password = request.headers.get('X-HKA-Password')
    return (token_empresa == VALID_TOKEN_EMPRESA and token_password == VALID_TOKEN_PASSWORD)

# ===========================
#  Función para registrar logs
# ===========================
def log_request(response_data=None):
    data = request.get_json() if request.method == 'POST' else dict(request.args)
    new_log = {
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'method': request.method,
        'path': request.path,
        'data': data,
        'response': response_data or {}
    }
    with log_lock:
        LOGS.append(new_log)
        try:
            with open(LOG_FILE, 'w') as f:
                json.dump(LOGS, f, indent=2)
        except IOError as e:
            print(f"Error writing to log file: {e}")

# ===========================
#  Rutas principales
# ===========================
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    with log_lock:
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    current_logs = json.load(f)
            else:
                current_logs = []
        except (IOError, json.JSONDecodeError):
            current_logs = []
    return render_template_string(DASHBOARD_TEMPLATE, logs=current_logs)

@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    global LOGS
    with log_lock:
        LOGS = []
        if os.path.exists(LOG_FILE):
            try:
                os.remove(LOG_FILE)
            except OSError as e:
                print(f"Error removing log file: {e}")
    return redirect(url_for('dashboard'))

@app.route('/api/logs', methods=['GET'])
def api_get_logs():
    if not check_auth():
        return unauthorized()
    with log_lock:
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    current_logs = json.load(f)
            else:
                current_logs = []
        except (IOError, json.JSONDecodeError):
            current_logs = []
    return jsonify(current_logs)

# ===========================
#  Endpoints fiscales
# ===========================
SAMPLE_DATA = {
    "status": "OK",
    "message": "",
    "data": {
        "nroFiscal": 12345,
        "serial": "ABC123456",
        "fecha": "2025-07-01 12:00",
        "ultimoZ": 99,
    }
}

def unauthorized():
    resp = {"status": 401, "message": "Unauthorized: Invalid tokens"}
    log_request(resp)
    return jsonify(resp), 401

@app.route('/api/imprimir/factura', methods=['POST'])
def imprimir_factura():
    if not check_auth():
        return unauthorized()
    data = request.get_json() or {}
    resp = SAMPLE_DATA.copy()
    resp['received'] = data
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/factura', methods=['GET'])
def reimprimir_factura():
    if not check_auth():
        return unauthorized()
    resp = {"status": "OK", "message": ""}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/nota-credito', methods=['POST'])
def nota_credito():
    if not check_auth():
        return unauthorized()
    data = request.get_json() or {}
    resp = SAMPLE_DATA.copy()
    resp['received'] = data
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/nota-credito', methods=['GET'])
def reimprimir_nota():
    if not check_auth():
        return unauthorized()
    resp = {"status": "OK", "message": ""}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/no-fiscal', methods=['POST'])
def no_fiscal():
    if not check_auth():
        return unauthorized()
    resp = {"status": "OK", "message": ""}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/reporte_x', methods=['GET', 'POST'])
def reporte_x():
    if not check_auth():
        return unauthorized()
    log_request(SAMPLE_DATA)
    return jsonify(SAMPLE_DATA)

@app.route('/api/imprimir/reporte_z', methods=['GET', 'POST'])
def reporte_z():
    if not check_auth():
        return unauthorized()
    log_request(SAMPLE_DATA)
    return jsonify(SAMPLE_DATA)

@app.route('/api/data_z', methods=['GET'])
def data_z():
    if not check_auth():
        return unauthorized()
    resp = {
        "status": "OK", "message": "", "data": {
            "numero_ultima_factura": "100",
            "ventas_exento": 0.0,
        }
    }
    log_request(resp)
    return jsonify(resp)

@app.route('/api/data/data_numeracion', methods=['GET'])
def data_numeracion():
    if not check_auth():
        return unauthorized()
    resp = {
        "status": "OK", "message": "",
        "data": {"ultimaFactura": 101, "ultimaNotaCredito": 5, "ultimoDocumentoNoFiscal": 20, "ultimoZ": 100}
    }
    log_request(resp)
    return jsonify(resp)

@app.route('/api/send-raw', methods=['POST'])
def send_raw():
    if not check_auth():
        return unauthorized()
    resp = {"status": "OK", "message": ""}
    log_request(resp)
    return jsonify(resp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
