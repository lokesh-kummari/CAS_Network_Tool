import subprocess
import time
import os
import http.server
import socketserver
import threading

def start_server(script_path):
    return subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_html_server(directory, port):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    print(f"Serving HTML at http://127.0.0.1:{port}/")
    httpd.serve_forever()

if __name__ == '__main__':
    # Paths to your Flask app scripts
    script1_path = "C:/Users/ADMIN/Downloads/Network-Monitoring-ujjsent/Network-Monitoring-ujjsent/app.py"
    script2_path = "C:/Users/ADMIN/Downloads/Network-Monitoring-ujjsent/Network-Monitoring-ujjsent/app1.py"
    script3_path = "C:/Users/ADMIN\Downloads/Network-Monitoring-ujjsent/Network-Monitoring-ujjsent/bandwidthusage.py"
    script4_path = "C:/Users/ADMIN/Downloads/Network-Monitoring-ujjsent/Network-Monitoring-ujjsent/networktopo.py"

    html_directory = "C:/Users/ADMIN/Downloads/Network-Monitoring-ujjsent/Network-Monitoring-ujjsent/templates"
    html_port = 3000

    # Check if the paths exist
    if not os.path.isfile(script1_path):
        print(f"Error: {script1_path} does not exist.")
    if not os.path.isfile(script2_path):
        print(f"Error: {script2_path} does not exist.")
    if not os.path.isfile(script3_path):
        print(f"Error: {script3_path} does not exist.")
    if not os.path.isdir(html_directory):
        print(f"Error: {html_directory} does not exist.")

    # Start Flask servers
    server1 = start_server(script1_path)
    server2 = start_server(script2_path)
    server3 = start_server(script3_path)
    server4 = start_server(script4_path)

    # Start HTML server in a separate thread
    threading.Thread(target=start_html_server, args=(html_directory, html_port)).start()

    # Give the servers a few seconds to start
    time.sleep(5)

    # Check if the servers are still running
    if server1.poll() is not None:
        print("Flask Server 1 encountered an error:")
        print(server1.stderr.read().decode())

    if server2.poll() is not None:
        print("Flask Server 2 encountered an error:")
        print(server2.stderr.read().decode())

    print("All servers are running")
    print("Flask Server 1: http://127.0.0.1:5000/")
    print("Flask Server 2: http://127.0.0.1:8000/")
    print("Flask server 3: http://127.0.0.1:5001/")
    print("Flask server 4: http://127.0.0.1:5002/")
    print(f"HTML Server: http://127.0.0.1:{html_port}/home.html")
