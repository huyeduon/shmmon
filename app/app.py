
from flask import Flask, render_template
import requests
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
apic = '192.168.8.2'

# Replace this URL with your actual API endpoint
LOGIN_API_ENDPOINT = f'https://{apic}/api/aaaLogin.json'
MEMORY_API_ENDPOINT = f'https://{apic}/api/node/mo/topology/pod-1/node-102/sys/eqptcapacity/fspartition-dev:shm.json?query-target=self'

# Replace 'your_username' and 'your_password' with your actual credentials
USERNAME = 'admin'
PASSWORD = '12345C1scoUC$'

def authenticate():
    data = {
        'aaaUser': {
            'attributes': {
                'name': USERNAME,
                'pwd': PASSWORD
            }
        }
    }

    response = requests.post(LOGIN_API_ENDPOINT, json=data, verify=False)
    response.raise_for_status()
    auth_token = response.json().get('imdata', [{}])[0].get('aaaLogin', {}).get('attributes', {}).get('token', '')
    return auth_token

def get_memory_data(auth_token):
    headers = {'Cookie': f'APIC-cookie={auth_token}'}
    memory_response = requests.get(MEMORY_API_ENDPOINT, headers=headers, verify=False)
    memory_response.raise_for_status()
    return memory_response.json()

def calculate_utilization_color(memory_data):
    used = float(memory_data['imdata'][0]['eqptcapacityFSPartition']['attributes']['used'])
    avail = float(memory_data['imdata'][0]['eqptcapacityFSPartition']['attributes']['avail'])
    utilization_percentage = (used / (used + avail)) * 100
    #utilization_percentage = 84
    if utilization_percentage > 85:
        color = 'red'
        font_weight = 'bold'
    else:
        color = 'green'
        font_weight = 'normal'
    return utilization_percentage, color, font_weight

@app.route('/')
def index():
    auth_token = authenticate()
    memory_data = get_memory_data(auth_token)
    utilization_percentage, color, font_weight = calculate_utilization_color(memory_data)

    return render_template('index.html', avail=memory_data['imdata'][0]['eqptcapacityFSPartition']['attributes']['avail'],
                           used=memory_data['imdata'][0]['eqptcapacityFSPartition']['attributes']['used'],
                           utilization_percentage=utilization_percentage, color=color, font_weight=font_weight)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)