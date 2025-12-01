import subprocess, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))

def start_tor():
    tor_path = os.path.join(PROJECT_ROOT,"Networking", "tor", "tor.exe")
    subprocess.Popen([
        tor_path],
        creationflags= subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )