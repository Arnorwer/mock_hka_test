from flask import Flask, request, jsonify, redirect, url_for
from datetime import datetime
import os, json, threading

app = Flask(__name__)

VALID_TOKEN_EMPRESA = "abcd1234"
VALID_TOKEN_PASSWORD = "abcd1234"
LOGS = []
LOG_FILE = 'request_logs.json'
log_lock = threading.Lock()

# Carga inicial de logs
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'r') as f:
        try:
            LOGS = json.load(f)
        except:
            LOGS = []

def unauthorized():
    resp = {'status': 401, 'message': 'Unauthorized: Invalid tokens'}
    log_request(resp)
    return jsonify(resp), 401

def check_auth():
    return (request.headers.get('X-printer-Token') == VALID_TOKEN_EMPRESA
            and request.headers.get('X-printer-Password') == VALID_TOKEN_PASSWORD)

def log_request(response_data=None):
    entry = {
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'method': request.method,
        'path': request.path,
        'data': request.get_json() if request.method=='POST' else dict(request.args),
        'response': response_data or {}
    }
    with log_lock:
        LOGS.append(entry)
        with open(LOG_FILE, 'w') as f:
            json.dump(LOGS, f, indent=2)

# Plantilla completa de datos para Reporte Z
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
    'nota_de_debito_exento': 0.0,
    'bi_iva_g_en_nota_de_debito': 0.0,
    'impuesto_iva_g_en_nota_de_debito': 0.0,
    'bi_iva_r_en_nota_de_debito': 0.0,
    'impuesto_iva_r_en_nota_de_debito': 0.0,
    'bi_iva_a_en_nota_de_debito': 0.0,
    'impuesto_iva_a_en_nota_de_debito': 0.0,
    'nota_de_credito_exento': 0.0,
    'bi_iva_g_en_nota_de_credito': 0.0,
    'impuesto_iva_g_en_nota_de_credito': 0.0,
    'bi_iva_r_en_nota_de_credito': 0.0,
    'impuesto_iva_r_en_nota_de_credito': 0.0,
    'bi_iva_a_en_nota_de_credito': 0.0,
    'impuesto_iva_a_en_nota_de_credito': 0.0,
    'numero_impresora': 'ABC123456',
    'bi_igtf_en_factura': 0.0,
    'impuesto_igtf_en_factura': 0.0,
    'bi_igtf_en_nota_de_credito': 0.0,
    'impuesto_igtf_en_nota_de_credito': 0.0,
}

# --- ENDPOINTS FISCALES ---

@app.route('/api/imprimir/factura', methods=['POST'])
def imprimir_factura():
    if not check_auth(): return unauthorized()
    p = request.get_json() or {}
    now = datetime.now()
    nro = int(now.timestamp()) % 100000
    resp = {
        'status': 'OK', 'message': '',
        'data': {
            'nroFiscal': nro,
            'serial': p.get('backendRef', f"SER{nro}"),
            'fecha': now.strftime("%Y-%m-%d %H:%M"),
            'ultimoZ': 99
        }
    }
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/factura', methods=['GET'])
def reimprimir_factura():
    if not check_auth(): return unauthorized()
    try:
        start, end = int(request.args['numDesde']), int(request.args['numHasta'])
    except:
        start = end = 0
    data = list(range(start, end+1))
    resp = {'status':'OK','message':'','data':data}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/nota-credito', methods=['POST'])
def imprimir_nota_credito():
    if not check_auth(): return unauthorized()
    p = request.get_json() or {}
    now = datetime.now()
    nro = int(now.timestamp()) % 100000
    resp = {
        'status':'OK','message':'',
        'data': {
            'nroFiscal': nro,
            'serial': p.get('serial', f"NC{nro}"),
            'fecha': now.strftime("%Y-%m-%d %H:%M"),
            'ultimoZ': 99
        }
    }
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/nota-credito', methods=['GET'])
def reimprimir_nota_credito():
    if not check_auth(): return unauthorized()
    try:
        start, end = int(request.args['numDesde']), int(request.args['numHasta'])
    except:
        start = end = 0
    data = list(range(start, end+1))
    resp = {'status':'OK','message':'','data':data}
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
            'ultimoZ': 99
        }
    }
    log_request(resp)
    return jsonify(resp)

@app.route('/api/imprimir/reporte_z', methods=['GET','POST'])
def reporte_z():
    if not check_auth(): return unauthorized()
    args = request.args
    # Reimpresión por número
    if request.method=='GET' and 'numDesde' in args and 'numHasta' in args:
        try:
            start = int(args['numDesde']); end = int(args['numHasta'])
        except:
            start = end = 0
        resp = {'status':'OK','message':'','data': list(range(start, end+1))}
    # Reimpresión por fecha
    elif request.method=='GET' and 'fechaDesde' in args and 'fechaHasta' in args:
        resp = {'status':'OK','message':'','data': {'fechaDesde': args['fechaDesde'], 'fechaHasta': args['fechaHasta']}}
    # Impresión inicial o POST
    else:
        resp = {'status':'OK','message':'','data': REPORT_Z_SUMMARY}
    log_request(resp)
    return jsonify(resp)
@app.route('/api/data_z', methods=['GET'])
def data_z():
    if not check_auth(): return unauthorized()
    # Consulta de reporte Z específico
    resp = {'status':'OK','message':'','data': REPORT_Z_SUMMARY}
    log_request(resp)
    return jsonify(resp)

@app.route('/api/data/data_numeracion', methods=['GET'])
def data_numeracion():
    if not check_auth(): return unauthorized()
    resp = {'status':'OK','message':'','data':{'ultimaFactura':101,'ultimaNotaCredito':5,'ultimoDocumentoNoFiscal':20,'ultimoZ':100}}
    log_request(resp)
    return jsonify(resp)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)