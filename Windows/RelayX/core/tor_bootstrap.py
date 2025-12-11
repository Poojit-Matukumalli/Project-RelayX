import subprocess, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))

def start_tor():
    tor_path = os.path.join(PROJECT_ROOT,"Networking", "tor", "tor.exe")
    torrc_path = os.path.join(PROJECT_ROOT, "Networking", "tor", "torrc")
    subprocess.Popen([tor_path, "-f", torrc_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=0 
    )