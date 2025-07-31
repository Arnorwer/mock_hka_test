from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

# Almacén en memoria de peticiones para el dashboard
LOGS = []

# Plantilla HTML para el dashboard
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
      {% for idx, entry in logs|reverse|enumerate(start=1) %}
      <tr>
        <td>{{ idx }}</td>
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
    return jsonify({"status":"OK","message":""})

@app.route('/api/imprimir/no-fiscal', methods=['POST'])
def no_fiscal():
    log_request()
    return jsonify({"status":"OK","message":""})

@app.route('/api/imprimir/reporte_x', methods=['GET', 'POST'])
def reporte_x():
    log_request()
    return jsonify({
        "status": "OK", "message": "", "data": {
            "nroFiscal": 12345,
            "serial": "ABC123456",
            "fecha": "2025-07-01 12:00",
            "ultimoZ": 99
        }
    })

@app.route('/api/imprimir/reporte_z', methods=['GET', 'POST'])
def reporte_z():
    log_request()
    return jsonify({
        "status": "OK", "message": "", "data": {
            "nroFiscal": 12345,
            "serial": "ABC123456",
            "fecha": "2025-07-01 12:00",
            "ultimoZ": 99
        }
    })

@app.route('/api/data_z', methods=['GET'])
def data_z():
    log_request()
    return jsonify({
        "status":"OK","message":"","data":{
            "numero_ultima_factura":"100",
            "ventas_exento":0.0,
            # …otros campos según spec…
        }
    })

@app.route('/api/data/data_numeracion', methods=['GET'])
def data_numeracion():
    log_request()
    return jsonify({
        "status":"OK","message":"",
        "data":{"ultimaFactura":101,"ultimaNotaCredito":5,"ultimoDocumentoNoFiscal":20,"ultimoZ":100}
    })

@app.route('/api/send-raw', methods=['POST'])
def send_raw():
    log_request()
    return jsonify({"status":"OK","message":""})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
