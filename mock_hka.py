
from flask import Flask, request, jsonify, redirect, url_for
from datetime import datetime
import os

from log_storage import append_log
from dashboard import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)

# Datos de ejemplo para las respuestas
SAMPLE_DATA = {
    "status": "OK",
    "message": "",
    "data": {
        "nroFiscal": 12345,
        "serial": "ABC123456",
        "fecha": "2025-07-01 12:00",
        "ultimoZ": 99
    }
}

def log_request():
    """Registra la petición entrante usando log_storage."""
    data = request.get_json() if request.method == 'POST' else dict(request.args)
    append_log({
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'method': request.method,
        'path': request.path,
        'data': data
    })
 
@app.route('/', methods=['GET', 'HEAD'])
def index():
    # Redirige al dashboard principal
    return redirect(url_for('dashboard_bp.dashboard'))
 
@app.route('/api/imprimir/factura', methods=['POST'])
def imprimir_factura():
    log_request()
    return jsonify(SAMPLE_DATA)
 
@app.route('/api/imprimir/factura', methods=['GET'])
def reimprimir_factura():
    log_request()
    return jsonify({"status": "OK", "message": ""})
 
@app.route('/api/imprimir/nota-credito', methods=['POST'])
def nota_credito():
    log_request()
    return jsonify(SAMPLE_DATA)
 
@app.route('/api/imprimir/nota-credito', methods=['GET'])
def reimprimir_nota():
    log_request()
    return jsonify({"status": "OK", "message": ""})
 
@app.route('/api/imprimir/no-fiscal', methods=['POST'])
def no_fiscal():
    log_request()
    return jsonify({"status": "OK", "message": ""})
 
@app.route('/api/imprimir/reporte_x', methods=['GET', 'POST'])
def reporte_x():
    log_request()
    return jsonify(SAMPLE_DATA)
 
@app.route('/api/imprimir/reporte_z', methods=['GET', 'POST'])
def reporte_z():
    log_request()
    return jsonify(SAMPLE_DATA)
 
@app.route('/api/data_z', methods=['GET'])
def data_z():
    log_request()
    return jsonify({
        "status": "OK", "message": "", "data": {
            "numero_ultima_factura": "100",
            "ventas_exento": 0.0
        }
    })
 
@app.route('/api/data/data_numeracion', methods=['GET'])
def data_numeracion():
    log_request()
    return jsonify({
        "status": "OK", "message": "",
        "data": {
            "ultimaFactura": 101,
            "ultimaNotaCredito": 5,
            "ultimoDocumentoNoFiscal": 20,
            "ultimoZ": 100
        }
    })
 
@app.route('/api/send-raw', methods=['POST'])
def send_raw():
    log_request()
    return jsonify({"status": "OK", "message": ""})
from flask import Flask, request, jsonify, redirect, url_for
from datetime import datetime
from log_storage import append_log
from dashboard import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)

def log_request():
    """Registra la petición entrante usando log_storage."""
    data = request.get_json() if request.method == 'POST' else dict(request.args)
    append_log({
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'method': request.method,
        'path': request.path,
        'data': data
    })

@app.route('/', methods=['GET', 'HEAD'])
def index():
    # Redirige al dashboard principal
    return redirect(url_for('dashboard_bp.dashboard'))
    return jsonify(SAMPLE_DATA)

@app.route('/api/imprimir/reporte_z', methods=['GET', 'POST'])
def reporte_z():
    log_request()
    return jsonify(SAMPLE_DATA)

@app.route('/api/data_z', methods=['GET'])
def data_z():
    log_request()
    return jsonify({
        "status":"OK","message":"","data":{
            "numero_ultima_factura":"100",
            "ventas_exento":0.0,
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
