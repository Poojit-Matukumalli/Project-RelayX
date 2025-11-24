import subprocess
import time
import os
import sys
import platform


def base_networking_dir():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base, 'Networking')


ROOT_DIR = base_networking_dir()
DATA_DIR = os.path.join(ROOT_DIR, "data", "tor_necessities")
HS_DIR = os.path.join(ROOT_DIR, "data", "HiddenService")


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

try:
    with open(os.path.join(HS_DIR, "hostname")) as f:
        onion = f.read() 
finally:
    try:
        proc.terminate()
    except Exception:
        pass
    except Exception as e:
        print(f"Error starting Tor hidden service: {e}")
        sys.exit(1)