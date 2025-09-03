from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from datetime import datetime
import os, json, threading

app = Flask(__name__)
# Do not sort JSON keys to preserve insertion order
app.config['JSON_SORT_KEYS'] = False

# Tokens fijos para pruebas
VALID_TOKEN_EMPRESA = "abcd1234"
VALID_TOKEN_PASSWORD = "abcd1234"

# Configuración de delay para simular servicio fiscal lento
DEFAULT_DELAY = 15  # segundos por defecto
SIMULATE_TIMEOUTS = False  # simular timeouts/errores

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
  <title>Dashboard Mock Fiscal Printer</title>
  <style>
    body { font-family: sans-serif; padding: 20px; background: #f5f5f5; }
    .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .test-panel { background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #2196f3; }
    .controls { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    th, td { border: 1px solid #e0e0e0; padding: 12px; text-align: left; vertical-align: top; }
    th { background: #f8f9fa; font-weight: 600; }
    tr:nth-child(even) { background: #fafafa; }
    pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; font-size: 11px; }
    .unauthorized { background-color: #ffe5e5; }
    .delay-test { background-color: #fff3e0; }
    .success { background-color: #e8f5e8; }
    button { padding: 8px 16px; margin: 2px; border: none; border-radius: 4px; cursor: pointer; }
    .btn-primary { background: #2196f3; color: white; }
    .btn-danger { background: #f44336; color: white; }
    .btn-success { background: #4caf50; color: white; }
    .test-links a { display: inline-block; margin: 5px; padding: 8px 12px; background: #2196f3; color: white; text-decoration: none; border-radius: 4px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🖨️ Mock Fiscal Printer Dashboard</h1>
    <p><strong>Estado:</strong> <span style="color: green;">🟢 Activo</span> | <strong>Tokens válidos:</strong> ✅</p>
  </div>

  <div class="test-panel">
    <h3>🧪 Panel de Pruebas de Reporte Z</h3>
    <p><strong>Simula el problema real:</strong> El servicio fiscal real tarda entre 15-90 segundos en responder al Reporte Z.</p>
    
    <div style="background: white; padding: 15px; border-radius: 6px; margin: 10px 0;">
      <h4>⚙️ Configurar Delay del Reporte Z</h4>
      <form id="delay-form" style="display: flex; align-items: center; gap: 10px;">
        <label for="delay-input">Delay (segundos):</label>
        <input type="number" id="delay-input" min="1" max="300" value="15" style="width: 80px; padding: 5px;">
        <button type="button" onclick="setDelay()" class="btn-primary">Aplicar</button>
        <span id="current-delay">Actual: 15s</span>
      </form>
      
      <div style="margin-top: 10px;">
        <button onclick="setDelay(5)" class="btn-success">Rápido (5s)</button>
        <button onclick="setDelay(15)" class="btn-primary">Normal (15s)</button>
        <button onclick="setDelay(45)" class="btn-primary">Lento (45s)</button>
        <button onclick="setDelay(90)" class="btn-danger">Extremo (90s)</button>
      </div>
      
      <div style="margin-top: 15px; padding: 10px; background: #f0f8ff; border-radius: 4px;">
        <strong>🎯 Control de Comunicación:</strong>
        <button onclick="enableTimeouts()" class="btn-danger" style="margin-left: 10px;">⚡ Simular Timeout/Error</button>
        <button onclick="disableTimeouts()" class="btn-success" style="margin-left: 10px;">✅ Comunicación Normal</button>
        <span id="timeout-status">Estado: Normal</span>
      </div>
    </div>
    
    <div class="test-links">
      <p><strong>Enlaces de prueba directa:</strong></p>
      <a href="/api/imprimir/reporte_z?delay=5" target="_blank">Prueba Rápida (5s)</a>
      <a href="/api/imprimir/reporte_z?delay=15" target="_blank">Prueba Normal (15s)</a>
      <a href="/api/imprimir/reporte_z?delay=45" target="_blank">Prueba Lenta (45s)</a>
      <a href="/api/imprimir/reporte_z?delay=90" target="_blank">Prueba Extrema (90s)</a>
    </div>
    <p><small>💡 <strong>Tip:</strong> Configura el delay arriba y luego prueba el cierre de sesión desde Odoo POS</small></p>
  </div>
  
  <div class="controls">
    <h3>📊 Controles</h3>
    <form action="/clear-logs" method="post" style="display: inline;">
        <button type="submit" class="btn-danger">🗑️ Limpiar Logs</button>
    </form>
    <button onclick="fetchLogs()" class="btn-primary">🔄 Actualizar</button>
    <button onclick="toggleAutoRefresh()" class="btn-success" id="toggle-btn">⏸️ Pausar Auto-actualización</button>
  </div>
  
  <table>
    <thead>
      <tr>
        <th>#</th><th>Timestamp</th><th>Método</th><th>Endpoint</th><th>Delay</th><th>Datos</th><th>Respuesta</th>
      </tr>
    </thead>
    <tbody id="log-table-body">
      {% for entry in logs|reverse %}
      <tr class="{% if entry.response.status == 401 %}unauthorized{% elif 'delay' in entry.path %}delay-test{% elif entry.response.status == 'OK' %}success{% endif %}">
        <td>{{ loop.index }}</td>
        <td>{{ entry.time }}</td>
        <td>{{ entry.method }}</td>
        <td>{{ entry.path }}</td>
        <td>{% if 'delay=' in entry.path %}{{ entry.path.split('delay=')[1].split('&')[0] }}s{% else %}-{% endif %}</td>
        <td><pre>{{ entry.data | tojson(indent=2) }}</pre></td>
        <td><pre>{{ entry.response | tojson(indent=2) }}</pre></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  <script>
    let autoRefresh = true;
    let refreshInterval;
    
    async function fetchLogs() {
      const res = await fetch('/api/logs');
      const logs = await res.json();
      const tbody = document.getElementById('log-table-body');
      tbody.innerHTML = '';
      logs.slice().reverse().forEach((entry, idx) => {
        const tr = document.createElement('tr');
        if (entry.response && entry.response.status == 401) {
            tr.classList.add('unauthorized');
        } else if (entry.path && entry.path.includes('delay=')) {
            tr.classList.add('delay-test');
        } else if (entry.response && entry.response.status == 'OK') {
            tr.classList.add('success');
        }
        
        // Extraer delay de la URL
        const delay = entry.path && entry.path.includes('delay=') 
          ? entry.path.split('delay=')[1].split('&')[0] + 's' 
          : '-';
          
        const cells = [idx+1, entry.time, entry.method, entry.path, delay];
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
    
    function toggleAutoRefresh() {
      const btn = document.getElementById('toggle-btn');
      if (autoRefresh) {
        clearInterval(refreshInterval);
        btn.textContent = '▶️ Reanudar Auto-actualización';
        btn.className = 'btn-success';
        autoRefresh = false;
      } else {
        refreshInterval = setInterval(fetchLogs, 2000);
        btn.textContent = '⏸️ Pausar Auto-actualización';
        btn.className = 'btn-success';
        autoRefresh = true;
      }
    }
    
    async function setDelay(seconds) {
      if (seconds === undefined) {
        seconds = document.getElementById('delay-input').value;
      }
      
      try {
        const res = await fetch(`/test/set-delay/${seconds}`, { method: 'POST' });
        const result = await res.json();
        
        if (result.status === 'OK') {
          document.getElementById('current-delay').textContent = `Actual: ${seconds}s`;
          document.getElementById('delay-input').value = seconds;
          
          // Mostrar notificación
          showNotification(`✅ Delay configurado a ${seconds} segundos`, 'success');
        } else {
          showNotification('❌ Error al configurar delay', 'error');
        }
      } catch (error) {
        showNotification('❌ Error de conexión', 'error');
      }
    }
    
    async function enableTimeouts() {
      try {
        const res = await fetch('/test/enable-timeouts', { method: 'POST' });
        const result = await res.json();
        
        if (result.status === 'OK') {
          document.getElementById('timeout-status').textContent = 'Estado: ⚡ Simulando Errores';
          document.getElementById('timeout-status').style.color = 'red';
          showNotification('⚡ Modo timeout/error activado', 'warning');
        }
      } catch (error) {
        showNotification('❌ Error de conexión', 'error');
      }
    }
    
    async function disableTimeouts() {
      try {
        const res = await fetch('/test/disable-timeouts', { method: 'POST' });
        const result = await res.json();
        
        if (result.status === 'OK') {
          document.getElementById('timeout-status').textContent = 'Estado: ✅ Normal';
          document.getElementById('timeout-status').style.color = 'green';
          showNotification('✅ Comunicación normal restaurada', 'success');
        }
      } catch (error) {
        showNotification('❌ Error de conexión', 'error');
      }
    }
    
    function showNotification(message, type) {
      const div = document.createElement('div');
      div.textContent = message;
      div.style.cssText = `
        position: fixed; top: 20px; right: 20px; z-index: 1000;
        padding: 12px 20px; border-radius: 4px; color: white; font-weight: 600;
        background: ${type === 'success' ? '#4caf50' : type === 'warning' ? '#ff9800' : '#f44336'};
      `;
      document.body.appendChild(div);
      setTimeout(() => div.remove(), 3000);
    }
    
    // Cargar estado inicial del delay
    async function loadCurrentDelay() {
      try {
        const res = await fetch('/test/status');
        const status = await res.json();
        if (status.current_delay) {
          document.getElementById('current-delay').textContent = `Actual: ${status.current_delay}s`;
          document.getElementById('delay-input').value = status.current_delay;
        }
      } catch (error) {
        console.log('No se pudo cargar el estado inicial');
      }
    }
    
    fetchLogs();
    loadCurrentDelay();
    refreshInterval = setInterval(fetchLogs, 2000);
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
    
    # Verificar si debemos simular timeout/error
    if SIMULATE_TIMEOUTS:
        import random
        if random.choice([True, False]):  # 50% chance de timeout
            resp = {'status': 'ERROR', 'message': 'Timeout: No se pudo conectar con el servicio fiscal'}
            log_request(resp)
            return jsonify(resp), 500
    
    # Simular el delay real del servicio fiscal (15-90 segundos)
    import time
    delay_seconds = request.args.get('delay', str(DEFAULT_DELAY))  # Usar delay global por defecto
    try:
        delay = int(delay_seconds)
    except:
        delay = DEFAULT_DELAY
    
    # Simular el procesamiento lento del servicio fiscal
    print(f"⏰ Iniciando Reporte Z - Simulando delay de {delay} segundos...")
    time.sleep(delay)
    print(f"✅ Reporte Z completado después de {delay} segundos")
    
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
        # Generar número de reporte Z incremental para simular reportes reales
        import time
        reporte_num = int(time.time()) % 1000  # Número único basado en timestamp
        
        updated_summary = REPORT_Z_SUMMARY.copy()
        updated_summary['numero_ultimo_reporte_z'] = reporte_num
        updated_summary['fecha_ultimo_reporte_z'] = datetime.now().strftime("%Y-%m-%d")
        updated_summary['hora_ultimo_reporte_z'] = datetime.now().strftime("%H:%M:%S")
        
        resp = {
            'status':'OK',
            'message':f'Reporte Z #{reporte_num} generado exitosamente después de {delay}s',
            'data': updated_summary
        }
    
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

# Endpoint de prueba para configurar delays
@app.route('/test/set-delay/<int:seconds>', methods=['POST'])
def set_default_delay(seconds):
    global DEFAULT_DELAY
    DEFAULT_DELAY = max(1, min(300, seconds))  # Limitar entre 1 y 300 segundos
    return jsonify({
        'status': 'OK',
        'message': f'Delay por defecto configurado a {DEFAULT_DELAY} segundos',
        'delay': DEFAULT_DELAY
    })

@app.route('/test/enable-timeouts', methods=['POST'])
def enable_timeouts():
    global SIMULATE_TIMEOUTS
    SIMULATE_TIMEOUTS = True
    return jsonify({
        'status': 'OK',
        'message': 'Simulación de timeouts/errores activada',
        'simulate_timeouts': SIMULATE_TIMEOUTS
    })

@app.route('/test/disable-timeouts', methods=['POST'])
def disable_timeouts():
    global SIMULATE_TIMEOUTS
    SIMULATE_TIMEOUTS = False
    return jsonify({
        'status': 'OK',
        'message': 'Simulación de timeouts/errores desactivada',
        'simulate_timeouts': SIMULATE_TIMEOUTS
    })

@app.route('/test/status', methods=['GET'])
def test_status():
    return jsonify({
        'status': 'OK',
        'service': 'Mock Fiscal Printer',
        'version': '1.0',
        'timestamp': datetime.now().isoformat(),
        'current_delay': DEFAULT_DELAY,
        'simulate_timeouts': SIMULATE_TIMEOUTS,
        'endpoints': {
            'reporte_z': '/api/imprimir/reporte_z',
            'reporte_x': '/api/imprimir/reporte_x',
            'factura': '/api/imprimir/factura',
            'dashboard': '/dashboard'
        },
        'test_urls': {
            'quick_test': '/api/imprimir/reporte_z?delay=5',
            'slow_test': '/api/imprimir/reporte_z?delay=90',
            'normal_test': f'/api/imprimir/reporte_z?delay={DEFAULT_DELAY}'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)