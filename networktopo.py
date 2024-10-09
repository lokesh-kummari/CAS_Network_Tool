# Description: This script scans the network for devices and creates a network topology graph.
import scapy.all as scapy
import networkx as nx
import plotly.graph_objects as go
import pandas as pd
import math
from flask import Flask, render_template

app = Flask(__name__)

def get_mac_ip_pairs():
    """Scans the network and returns a list of IP and MAC addresses."""
    ip_range = "192.168.1.1/24"  # Adjust the IP range to your local network
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=10, verbose=False , inter=0.1)[0]

    devices = []
    for element in answered_list:
        devices.append({
            'ip': element[1].psrc,
            'mac': element[1].hwsrc
        })

    return devices

def create_network_graph(devices, topology_type='star'):
    """Creates and visualizes a network graph using networkx and Plotly."""
    G = nx.Graph()

    for device in devices:
        G.add_node(device['ip'], label=device['mac'])

    if topology_type == 'bus':
        for i in range(len(devices) - 1):
            G.add_edge(devices[i]['ip'], devices[i + 1]['ip'], weight=1)
        pos = {device['ip']: (i, 0) for i, device in enumerate(devices)}

    elif topology_type == 'star':
        central_node = devices[0]['ip']
        for device in devices[1:]:
            G.add_edge(central_node, device['ip'], weight=1)
        pos = {devices[0]['ip']: (0, 0)}
        angle_step = 2 * math.pi / (len(devices) - 1)
        for i, device in enumerate(devices[1:]):
            angle = i * angle_step
            pos[device['ip']] = (math.cos(angle), math.sin(angle))

    elif topology_type == 'ring':
        for i in range(len(devices)):
            G.add_edge(devices[i]['ip'], devices[(i + 1) % len(devices)]['ip'], weight=1)
        angle_step = 2 * math.pi / len(devices)
        pos = {device['ip']: (math.cos(i * angle_step), math.sin(i * angle_step)) for i, device in enumerate(devices)}

    else:
        print(f"Topology type '{topology_type}' not supported.")
        return

    # Create a DataFrame for Plotly
    node_data = pd.DataFrame({
        'ip': [device['ip'] for device in devices],
        'mac': [device['mac'] for device in devices],
        'x': [pos[device['ip']][0] for device in devices],
        'y': [pos[device['ip']][1] for device in devices]
    })

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_trace = go.Scatter(
        x=node_data['x'], y=node_data['y'],
        mode='markers+text',
        text=[f"{ip}<br>{mac}" for ip, mac in zip(node_data['ip'], node_data['mac'])],
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='Viridis',
            size=20,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=f'{topology_type.capitalize()} Topology',
                        titlefont=dict(size=24),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=60),
                        annotations=[dict(
                            text=f"{topology_type.capitalize()} Topology Visualization",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002
                        )],
                        xaxis=dict(showgrid=False, zeroline=False, title='X Coordinate'),
                        yaxis=dict(showgrid=False, zeroline=False, title='Y Coordinate'))
                    )
    fig.update_layout(
        font_family="Courier New",
        font_size=16,
        xaxis_title="X Axis",
        yaxis_title="Y Axis",
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        )
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')

@app.route('/')
def index():
    devices = get_mac_ip_pairs()
    if not devices:
        return "No devices found."
    
    num_devices = len(devices)
    if num_devices < 1:
        return "Not enough devices found to create a network topology."
    elif num_devices == 2:
        topology_type = 'bus'
    elif num_devices == 3:
        topology_type = 'star'
    else:
        topology_type = 'ring'

    return create_network_graph(devices, topology_type)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5002)
