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
    now = datetime.now()
    z = 99
    if request.method=='GET':
        if 'numDesde' in request.args and 'numHasta' in request.args:
            try:
                s,e = int(request.args['numDesde']),int(request.args['numHasta'])
            except: s=e=0
            data = list(range(s,e+1))
        elif 'fechaDesde' in request.args and 'fechaHasta' in request.args:
            data = {'fechaDesde':request.args['fechaDesde'],'fechaHasta':request.args['fechaHasta']}
        else:
            data = {
                'numero_ultimo_reporte_z': z,
                'fecha_ultimo_reporte_z': now.strftime("%Y-%m-%d"),
                'hora_ultimo_reporte_z': now.strftime("%H:%M"),
                'numero_ultima_factura': str(z+1),
                'numero_impresora': 'ABC123456'
            }
    else:
        data = {
            'numero_ultimo_reporte_z': z,
            'fecha_ultimo_reporte_z': now.strftime("%Y-%m-%d"),
            'hora_ultimo_reporte_z': now.strftime("%H:%M"),
            'numero_ultima_factura': str(z+1),
            'numero_impresora': 'ABC123456'
        }
    resp = {'status':'OK','message':'','data':data}
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