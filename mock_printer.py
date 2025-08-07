from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from datetime import datetime
import os, json, threading

app = Flask(__name__)

# Tokens fijos para pruebas
VALID_TOKEN_EMPRESA = "abcd1234"
VALID_TOKEN_PASSWORD = "abcd1234"

# Logs en memoria y en disco
LOGS = []
LOG_FILE = 'request_logs.json'
log_lock = threading.Lock()

# Carga inicial de logs
if os.path.exists(LOG_FILE):
    try:
        with open(LOG_FILE, 'r') as f:
            LOGS = json.load(f)
    except (IOError, json.JSONDecodeError):
        LOGS = []

# Dashboard HTML
DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Dashboard Mock printer</title>
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
  <h1>Dashboard Mock printer</h1>
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
      <tr class="{% if entry.response.status == 401 %}unauthorized{% endif %}">
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
        const cells = [idx+1, entry.time, entry.method, entry.path];
        cells.forEach(text => {
          const td = document.createElement('td');
          td.textContent = text;
          tr.appendChild(td);
        });
        const preData = document.createElement('pre');
        preData.textContent = JSON.stringify(entry.data, null, 2);
        const preResp = document.createElement('pre');
        preResp.textContent = JSON.stringify(entry.response, null, 2);
        const dataTd = document.createElement('td');
        dataTd.appendChild(preData);
        tr.appendChild(dataTd);
        const respTd = document.createElement('td');
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

# Payloads de ejemplo
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
REPORT_Z_SUMMARY = {
    'numero_ultimo_reporte_z': 100,
    'fecha_ultimo_reporte_z': '2025-07-01',
    'hora_ultimo_reporte_z': '12:00',
    'numero_ultima_factura': '101',
    'fecha_ultima_factura': '2025-07-01',
    'hora_ultima_factura': '12:05',
    'numero_ultima_nota_de_debito': '102',
    'numero_ultima_nota_de_credito': '103',
    'numero_ultimo_doc_no_fiscal': '104',
    'ventas_exento': 0.0,
    'base_imponible_ventas_iva_g': 100.0,
    'impuesto_iva_g': 16.0,
    'base_imponible_ventas_iva_r': 50.0,
    'impuesto_iva_r': 8.0,
    'base_imponible_ventas_iva_a': 20.0,
    'impuesto_iva_a': 31.0,
    # ... resto de campos como antes ...
    'impuesto_igtf_en_nota_de_credito': 0.0,
}

# Helpers
def check_auth():
    return (request.headers.get('X-printer-Token') == VALID_TOKEN_EMPRESA
            and request.headers.get('X-printer-Password') == VALID_TOKEN_PASSWORD)

def log_request(resp=None):
    entry = {
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'method': request.method,
        'path': request.path,
        'data': request.get_json() if request.method=='POST' else dict(request.args),
        'response': resp or {}
    }
    with log_lock:
        LOGS.append(entry)
        with open(LOG_FILE, 'w') as f:
            json.dump(LOGS, f, indent=2)

def unauthorized():
    resp = {'status': 401, 'message': 'Unauthorized: Invalid tokens'}
    log_request(resp)
    return jsonify(resp), 401

# Rutas de dashboard
@app.route('/', methods=['GET','HEAD'])
def index():
    return redirect(url_for('dashboard'))

@app.route('/api/send-raw', methods=['POST'])
def send_raw():
    if not check_auth():
        return unauthorized()
    resp = {'status':'OK', 'message':''}
    log_request(resp)
    return jsonify(resp)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    with log_lock:
        try:
            current_logs = json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
        except:
            current_logs = []
    return render_template_string(DASHBOARD_TEMPLATE, logs=current_logs)

@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    global LOGS
    with log_lock:
        LOGS = []
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
    return redirect(url_for('dashboard'))

@app.route('/api/logs', methods=['GET'])
def api_get_logs():
    # Auth sólo si vienen cabeceras
    if request.headers.get('X-printer-Token') or request.headers.get('X-printer-Password'):
        if not check_auth():
            return unauthorized()
    with log_lock:
        try:
            current_logs = json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []
        except:
            current_logs = []
    return jsonify(current_logs)

# Endpoints fiscales
@app.route('/api/imprimir/factura', methods=['POST'])
def imprimir_factura():
    if not check_auth(): return unauthorized()
    payload = request.get_json() or {}
    now = datetime.now()
    nro = int(now.timestamp()) % 100000
    resp = {
        'status':'OK','message':'',
        'data': {
            'nroFiscal': nro,
            'serial': payload.get('backendRef', f"SER{nro}"),
            'fecha': now.strftime("%Y-%m-%d %H:%M"),
            'ultimoZ': SAMPLE_DATA['data']['ultimoZ']
        }
    }
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/factura', methods=['GET'])
def reimprimir_factura():
    if not check_auth(): return unauthorized()
    try:
        start = int(request.args['numDesde']); end = int(request.args['numHasta'])
    except:
        start = end = 0
    resp = {'status':'OK','message':'','data': list(range(start, end+1))}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/nota-credito', methods=['POST'])
def imprimir_nota_credito():
    if not check_auth(): return unauthorized()
    payload = request.get_json() or {}
    now = datetime.now()
    nro = int(now.timestamp()) % 100000
    resp = {
        'status':'OK','message':'',
        'data': {
            'nroFiscal': nro,
            'serial': payload.get('serial', f"NC{nro}"),
            'fecha': now.strftime("%Y-%m-%d %H:%M"),
            'ultimoZ': SAMPLE_DATA['data']['ultimoZ']
        }
    }
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/nota-credito', methods=['GET'])
def reimprimir_nota_credito():
    if not check_auth(): return unauthorized()
    try:
        start = int(request.args['numDesde']); end = int(request.args['numHasta'])
    except:
        start = end = 0
    resp = {'status':'OK','message':'','data': list(range(start, end+1))}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/no-fiscal', methods=['POST'])
def no_fiscal():
    if not check_auth(): return unauthorized()
    resp = {'status':'OK','message':''}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/reporte_x', methods=['GET','POST'])
def reporte_x():
    if not check_auth(): return unauthorized()
    now = datetime.now()
    nro = int(now.timestamp()) % 100000
    resp = {
        'status':'OK','message':'',
        'data': {
            'nroFiscal': nro,
            'serial': f"RX{nro}",
            'fecha': now.strftime("%Y-%m-%d %H:%M"),
            'ultimoZ': SAMPLE_DATA['data']['ultimoZ']
        }
    }
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/reporte_z', methods=['GET','POST'])
def reporte_z():
    if not check_auth(): return unauthorized()
    args = request.args
    # reimpresión por número
    if request.method=='GET' and 'numDesde' in args and 'numHasta' in args:
        try:
            s,e = int(args['numDesde']), int(args['numHasta'])
        except:
            s=e=0
        resp = {'status':'OK','message':'','data': list(range(s, e+1))}
    # reimpresión por fecha
    elif request.method=='GET' and 'fechaDesde' in args and 'fechaHasta' in args:
        resp = {'status':'OK','message':'','data': {'fechaDesde': args['fechaDesde'], 'fechaHasta': args['fechaHasta']}}
    else:
        resp = {'status':'OK','message':'','data': REPORT_Z_SUMMARY}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/data_z', methods=['GET'])
def data_z():
    if not check_auth(): return unauthorized()
    resp = {'status':'OK','message':'','data': REPORT_Z_SUMMARY}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/data/data_numeracion', methods=['GET'])
def data_numeracion():
    if not check_auth(): return unauthorized()
    resp = {
        'status':'OK','message':'',
        'data': {
            'ultimaFactura': 101,
            'ultimaNotaCredito': 5,
            'ultimoDocumentoNoFiscal': 20,
            'ultimoZ': 100
        }
    }
    log_request(resp)
    return jsonify(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)