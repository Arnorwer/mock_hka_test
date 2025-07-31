from flask import Blueprint, render_template_string, redirect, url_for, jsonify
from log_storage import load_logs, clear_logs as clear_logs_storage

# Blueprint para las rutas del dashboard
dashboard_bp = Blueprint('dashboard_bp', __name__)

# Plantilla HTML del dashboard
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
  </style>
</head>
<body>
  <h1>Dashboard Mock HKA</h1>
  <div class="controls">
    <p>Total de peticiones registradas: {{ logs|length }}</p>
    <form action="/clear-logs" method="post" style="display: inline;">
        <button type="submit">Clear Logs</button>
    </form>
  </div>
  <table>
    <thead>
      <tr>
        <th>#</th><th>Timestamp</th><th>Método</th><th>Endpoint</th><th>Datos</th>
      </tr>
    </thead>
    <tbody id="log-table-body">
      {% for entry in logs|reverse %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ entry.time }}</td>
        <td>{{ entry.method }}</td>
        <td>{{ entry.path }}</td>
        <td><pre>{{ entry.data | tojson(indent=2) }}</pre></td>
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
        const indexCell = document.createElement('td');
        indexCell.textContent = idx + 1;
        tr.appendChild(indexCell);
        ['time', 'method', 'path'].forEach(key => {
          const td = document.createElement('td');
          td.textContent = entry[key];
          tr.appendChild(td);
        });
        const dataTd = document.createElement('td');
        const pre = document.createElement('pre');
        pre.textContent = JSON.stringify(entry.data, null, 2);
        dataTd.appendChild(pre);
        tr.appendChild(dataTd);
        tbody.appendChild(tr);
      });
    }
    fetchLogs();
    setInterval(fetchLogs, 2000);
  </script>
</body>
</html>
"""

@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Renderiza la página del dashboard con los logs."""
    logs = load_logs()
    return render_template_string(DASHBOARD_TEMPLATE, logs=logs)

@dashboard_bp.route('/clear-logs', methods=['POST'])
def clear_logs():
    """Vacía los logs y redirige al dashboard."""
    clear_logs_storage()
    return redirect(url_for('dashboard_bp.dashboard'))

@dashboard_bp.route('/api/logs', methods=['GET'])
def get_logs():
    """Devuelve los logs en formato JSON para actualización en tiempo real."""
    logs = load_logs()
    return jsonify(logs)
