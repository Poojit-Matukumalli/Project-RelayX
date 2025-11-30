import subprocess
import time
import os
import platform


def base_networking_dir():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base, 'Networking')


ROOT_DIR = base_networking_dir()
DATA_DIR = os.path.join(ROOT_DIR, "data", "tor_necessities")
HS_DIR = os.path.join(ROOT_DIR, "data", "HiddenService")
hostname_dir = os.path.join(HS_DIR, "hostname")

if platform.system() == "Windows":
    TOR_EXE = os.path.join(ROOT_DIR, "tor", "tor.exe")
else:
    TOR_EXE = os.path.join(ROOT_DIR, "tor", "tor")


os.makedirs(HS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.isfile(TOR_EXE):
    raise FileNotFoundError(f"Tor executable not found: {TOR_EXE}")


proc = subprocess.Popen(
    [
        TOR_EXE,
        "--DataDirectory", DATA_DIR,
        "--HiddenServiceDir", HS_DIR,
        "--HiddenServicePort", f"5050 127.0.0.1:5050"
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )

timeout = 30
start = time.time()
while not os.path.exists(hostname_dir):
    if time.time() - start > timeout:
        proc.terminate()
        time.sleep(0.5)

with open(hostname_dir, "r") as f:
    onion = f.read().strip()
proc.terminate()