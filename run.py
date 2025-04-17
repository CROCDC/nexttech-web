from app import app
from prometheus_flask_exporter import PrometheusMetrics
import psutil

# Inicializar el exporter de Prometheus
metrics = PrometheusMetrics(app)
metrics.group_by = ['method', 'status', 'path']

# Métricas personalizadas
@metrics.gauge('memory_usage_bytes', 'Memory usage in bytes')
def memory_usage():
    return psutil.Process().memory_info().rss

@metrics.gauge('cpu_usage_percent', 'CPU usage in percent')
def cpu_usage():
    return psutil.Process().cpu_percent()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=160, debug=True) 