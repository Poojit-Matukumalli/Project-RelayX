import subprocess, os

def start_tor():
    tor_path = os.path.join("Windows","Networking", "tor", "tor.exe")
    subprocess.Popen([
        tor_path],
        creationflags= subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
start_tor()