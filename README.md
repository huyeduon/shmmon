# ACI Leaf Switch Dev/Shm Utilization Monitoring.

This code runs a Flask web-server, it auto call API to APIC and check for dev/shm utilization of the switch whose ID is define in .env file.

Should run it in python3 virtual environment. The website is auto refreshed by default in 300 seconds. To refresh frequency, go to file index.html in the folder app/templates/ replace 300 with number of second you want.

```
 <meta http-equiv="refresh" content="300" />
```

**Install environment**

```
pip install -r requirements.txt
```

**Create .env file**

Create a .env file home folder (same level with app folder.)

Sample .env content:

```
apic="192.168.20.100" # apic ip address (replace with your actual IP)
username="admin" # apic username
password="mysecurepassword"
nodeid="201" # node id of the node you want to monitor
site="Site-1"
flaskport="5001" # flask app port
```

**To run:**

```
python3 app.py
```

**Sample result showing on web-browser:**

:+1: Utilization number will be blinking if higher than 85%.

![Sample result leaf dev/shm information](/assets/images/utilization.png)
