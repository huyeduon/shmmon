
from flask import Flask, render_template
import os
import requests
from dotenv import load_dotenv
load_dotenv()

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a file handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the root logger
logging.getLogger('').addHandler(file_handler)


app = Flask(__name__)
# Add this line to serve static files
app.config['STATIC_FOLDER'] = 'static'

# Load infor from environment variable
apic = os.getenv("apic")
username = os.getenv("username")
password = os.getenv("password")
nodeid = os.getenv("nodeid")
flaskport = os.getenv("flaskport")

# Replace this URL with your actual API endpoint
LOGIN_API_ENDPOINT = f'https://{apic}/api/aaaLogin.json'
MEMORY_API_ENDPOINT = f'https://{apic}/api/node/mo/topology/pod-1/node-{nodeid}/sys/eqptcapacity/fspartition-dev:shm.json?query-target=self'

def authenticate():
    try:
        data = {
            'aaaUser': {
                    'attributes': {
                    'name': username,
                    'pwd': password
                }
            }
        }

        response = requests.post(LOGIN_API_ENDPOINT, json=data, verify=False)
        response.raise_for_status()
        auth_token = response.json().get('imdata', [{}])[0].get('aaaLogin', {}).get('attributes', {}).get('token', '')
        return auth_token
    except requests.exceptions.HTTPError as e:
        logging.error(f"An error occurred during authentication: {e}")
        raise  # Re-raise the exception to propagate it further

def get_memory_data(auth_token):
    try:
        headers = {'Cookie': f'APIC-cookie={auth_token}'}
        memory_response = requests.get(MEMORY_API_ENDPOINT, headers=headers, verify=False)
        memory_response.raise_for_status()
        return memory_response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"An error occurred during memory data retrieval: {e}")
        raise  # Re-raise the exception to propagate it further

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
    try:
        auth_token = authenticate()
        memory_data = get_memory_data(auth_token)
        utilization_percentage, color, font_weight = calculate_utilization_color(memory_data)

        return render_template('index.html', avail=memory_data['imdata'][0]['eqptcapacityFSPartition']['attributes']['avail'],
                           used=memory_data['imdata'][0]['eqptcapacityFSPartition']['attributes']['used'],
                           utilization_percentage=utilization_percentage, color=color, font_weight=font_weight)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return render_template('error.html', error_message="An unexpected error occurred.")
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=flaskport,debug=True)