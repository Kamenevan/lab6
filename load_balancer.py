from flask import Flask, jsonify, request, redirect, url_for, render_template
import requests
import threading
import time

app = Flask(__name__)

instances = []
with open("ports.txt", 'r') as f:
    ports = f.read().splitlines()
    for port in ports:
        if port.strip().isdigit():
            instances.append({"ip": "127.0.0.1", "port": int(port.strip()), "status": ""})

round_robin_index = 0


def check_health():
    global instances
    while True:
        for instance in instances:
            try:
                response = requests.get(f'http://{instance["ip"]}:{instance["port"]}/health', timeout=3)
                if response.status_code != 200:
                    instance["status"] = "Не работает"
                else:
                    instance["status"] = "Работает"
            except requests.exceptions.RequestException:
                instance["status"] = "Не работает"
        time.sleep(5)


@app.route('/health')
def health():
    active_instances = [instance for instance in instances if instance['status'] == 'Работает']
    return jsonify(instances=active_instances)


@app.route('/process')
def process():
    global round_robin_index
    active_instances = [instance for instance in instances if instance['status'] == 'Работает']

    if len(active_instances) == 0:
        return jsonify(error="Нет доступных приложений"), 503

    instance = active_instances[round_robin_index]
    round_robin_index = (round_robin_index + 1) % len(active_instances)

    response = requests.get(f'http://{instance["ip"]}:{instance["port"]}/process')
    return jsonify(response.json())


@app.route('/')
def index():
    return render_template('index.html', instances=instances)


@app.route('/add_instance', methods=['POST'])
def add_instance():
    ip = request.form['ip']
    port = int(request.form['port'])
    instances.append({"ip": ip, "port": port, "status": ''})
    with open('ports.txt', 'a') as f:
        f.write(f"{port}\n")
    return redirect(url_for('index'))


@app.route('/remove_instance', methods=['POST'])
def remove_instance():
    index = int(request.form['index'])
    index = index - 1
    if 0 <= index < len(instances):
        instances.pop(index)

        with open('ports.txt', 'w') as f:
            for instance in instances:
                f.write(f"{instance['port']}\n")
    return redirect(url_for('index'))


@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    global round_robin_index
    active_instances = [instance for instance in instances if instance['status'] == 'Работает']

    if len(active_instances) == 0:
        return jsonify(error="Нет доступных приложений"), 503

    instance = active_instances[round_robin_index]
    round_robin_index = (round_robin_index + 1) % len(active_instances)

    response = requests.request(
        method=request.method,
        url=f'http://{instance["ip"]}:{instance["port"]}/{path}',
        data=request.data,
        headers=request.headers,
        cookies=request.cookies
    )
    return (response.text, response.status_code, response.headers.items())


if __name__ == '__main__':
    threading.Thread(target=check_health, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
