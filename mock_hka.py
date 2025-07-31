from flask import Flask, request, jsonify

app = Flask(__name__)

# Ruta raíz para health check
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return jsonify({"status":"OK","message":"Mock HKA is up"}), 200

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

@app.route('/api/imprimir/factura', methods=['POST'])
def imprimir_factura():
    payload = request.get_json()
    print("Factura recibida:", payload)
    return jsonify(SAMPLE_DATA)

@app.route('/api/imprimir/nota-credito', methods=['POST'])
def nota_credito():
    payload = request.get_json()
    print("Nota de crédito recibida:", payload)
    return jsonify(SAMPLE_DATA)

@app.route('/api/imprimir/no-fiscal', methods=['POST'])
def no_fiscal():
    payload = request.get_json()
    print("No-fiscal recibida:", payload)
    return jsonify({"status":"OK","message":""})

@app.route('/api/imprimir/reporte_x', methods=['GET','POST'])
def reporte_x():
    return jsonify(SAMPLE_DATA)

@app.route('/api/imprimir/reporte_z', methods=['GET','POST'])
def reporte_z():
    return jsonify(SAMPLE_DATA)

@app.route('/api/imprimir/factura', methods=['GET'])
def reimprimir_factura():
    numDesde = request.args.get('numDesde')
    numHasta = request.args.get('numHasta')
    print(f"Reimprimir facturas de {numDesde} a {numHasta}")
    return jsonify({"status":"OK","message":""})

@app.route('/api/imprimir/nota-credito', methods=['GET'])
def reimprimir_nota():
    numDesde = request.args.get('numDesde')
    numHasta = request.args.get('numHasta')
    print(f"Reimprimir notas de crédito de {numDesde} a {numHasta}")
    return jsonify({"status":"OK","message":""})

@app.route('/api/data_z', methods=['GET'])
def data_z():
    numZ = request.args.get('numZ')
    print(f"Consulta data_z para reporte {numZ}")
    return jsonify({
        "status":"OK","message":"","data":{
            "numero_ultima_factura":"100",
            "ventas_exento":0.0,
            # …otros campos según spec…
        }
    })

@app.route('/api/data/data_numeracion', methods=['GET'])
def data_numeracion():
    return jsonify({
        "status":"OK","message":"",
        "data":{"ultimaFactura":101,"ultimaNotaCredito":5,"ultimoDocumentoNoFiscal":20,"ultimoZ":100}
    })

@app.route('/api/send-raw', methods=['POST'])
def send_raw():
    cmds = request.get_json()
    print("Comandos RAW:", cmds)
    return jsonify({"status":"OK","message":""})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
