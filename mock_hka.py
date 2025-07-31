from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

# Almacén en memoria de peticiones para el dashboard
LOGS = []

# Plantilla HTML para el dashboard (usando loop.index en lugar de enumerate)
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
  </style>
</head>
<body>
  <h1>Dashboard Mock HKA</h1>
  <p>Total de peticiones registradas: {{ logs|length }}</p>
  <table>
    <thead>
      <tr>
        <th>#</th><th>Timestamp</th><th>Método</th><th>Endpoint</th><th>Datos</th>
      </tr>
    </thead>
    <tbody>
      {% for entry in logs|reverse %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ entry.time }}</td>
        <td>{{ entry.method }}</td>
        <td>{{ entry.path }}</td>
        <td><pre>{{ entry.data }}</pre></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""

def log_request():
    """Registra la petición entrante en LOGS."""
    data = request.get_json() if request.method == 'POST' else dict(request.args)
    LOGS.append({
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'method': request.method,
        'path': request.path,
        'data': data
    })

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return jsonify({"status": "OK", "message": "Mock HKA is up"}), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE, logs=LOGS)

@app.route('/api/imprimir/factura', methods=['POST'])
def imprimir_factura():
    log_request()
    return jsonify({
        "status": "OK", "message": "", "data": {
            "nroFiscal": 12345,
            "serial": "ABC123456",
            "fecha": "2025-07-01 12:00",
            "ultimoZ": 99
        }
    })

@app.route('/api/imprimir/factura', methods=['GET'])
def reimprimir_factura():
    log_request()
    return jsonify({"status":"OK","message":""})

@app.route('/api/imprimir/nota-credito', methods=['POST'])
def nota_credito():
    log_request()
    return jsonify({
        "status": "OK", "message": "", "data": {
            "nroFiscal": 12345,
            "serial": "ABC123456",
            "fecha": "2025-07-01 12:00",
            "ultimoZ": 99
        }
    })

@app.route('/api/imprimir/nota-credito', methods=['GET'])
def reimprimir_nota():
    log_request()
    return jsonify
