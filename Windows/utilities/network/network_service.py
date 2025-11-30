import subprocess
import threading
import os
import time
import sys

# --- Paths ---
def base_networking_dir():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base, 'Networking')

ROOT_DIR = base_networking_dir()
DATA_DIR = os.path.join(ROOT_DIR, "data", "tor_necessities")
HS_DIR = os.path.join(ROOT_DIR, "data", "HiddenService")

if os.name == "nt":
    TOR_EXE = os.path.join(ROOT_DIR, "tor", "tor.exe")
else:
    TOR_EXE = os.path.join(ROOT_DIR, "tor", "tor")

os.makedirs(HS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

hostname_file = os.path.join(HS_DIR, "hostname")

tor_process = subprocess.Popen(
    [
        TOR_EXE,
        "--DataDirectory", DATA_DIR,
        "--HiddenServiceDir", HS_DIR,
        "--HiddenServicePort", "5050 127.0.0.1:5050"
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)


timeout = 60
start_time = time.time()

while not os.path.isfile(hostname_file):
    if time.time() - start_time > timeout:
        tor_process.terminate()
        raise RuntimeError("Tor failed to start within 60 seconds")
    time.sleep(0.5)

with open(hostname_file, "r") as f:
    onion_address = f.read().strip()
    tor_process.terminate()