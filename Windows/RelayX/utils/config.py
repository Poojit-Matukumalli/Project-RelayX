import os, json

ROTATE_INTERVAL = 600
ROTATE_AFTER_MESSAGES = 25
LISTEN_PORT = 5050
PROXY = ("127.0.0.1", 5050)
tor_path = os.path.abspath(os.path.join("Windows", "Networking", "tor", "tor.exe" ))
details_json = os.path.abspath(os.path.join("Windows", "utilities","network", "details.json"))
relay_file = os.path.abspath(os.path.join("Windows", "network", "relay_list.json"))

with open(details_json, "r") as f:
    data = json.load(f)
    Username = data["Username"]

username = Username