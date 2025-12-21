import subprocess, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))

tor_process : subprocess.Popen | None = None

def start_tor():
    global tor_process
    tor_path = os.path.join(PROJECT_ROOT,"Networking", "tor", "tor")
    torrc_path = os.path.join(PROJECT_ROOT, "Networking", "tor", "torrc")
    tor_process = subprocess.Popen([tor_path, "-f", torrc_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, 
    )

def stop_tor():
    global tor_process
    if tor_process is None:
        return
    
    try:
        tor_process.terminate()
        tor_process.wait(timeout=5)
    except Exception:
        tor_process.kill()
    finally:
        tor_process = None