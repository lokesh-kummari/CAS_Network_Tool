# app.py
from flask import Flask, jsonify, render_template
import psutil

app = Flask(__name__)
previous_stats = {}

def get_network_stats(previous_stats):
    net_io = psutil.net_io_counters(pernic=True)
    usage_stats = {}

    for interface, stats in net_io.items():
        if interface in previous_stats:
            sent = stats.bytes_sent - previous_stats[interface]['bytes_sent']
            recv = stats.bytes_recv - previous_stats[interface]['bytes_recv']

            usage_stats[interface] = {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'bytes_sent_sec': sent,
                'bytes_recv_sec': recv
            }
        else:
            usage_stats[interface] = {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'bytes_sent_sec': 0,
                'bytes_recv_sec': 0
            }

    return usage_stats

@app.route('/network_stats')
def network_stats():
    global previous_stats
    current_stats = get_network_stats(previous_stats)
    previous_stats = {interface: {
        'bytes_sent': data['bytes_sent'],
        'bytes_recv': data['bytes_recv']
    } for interface, data in current_stats.items()}
    return jsonify(current_stats)

@app.route('/')
def index():
    return render_template('index2.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Specify the port as 5001