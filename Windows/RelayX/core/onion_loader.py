import asyncio, subprocess, os
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))


async def load_onion():
    addr_file = os.path.join(PROJECT_ROOT, "Networking", "data", "HiddenService","hostname")
    network_service = os.path.abspath(os.path.join("Project-RelayX","Windows", "utilities" ,"network", "network_service.py"))
    if not os.path.exists(addr_file):
        subprocess.Popen(["python", network_service],
                creationflags= subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL         
        )
    for _ in range(50):
        if os.path.exists(addr_file):
            with open(addr_file, "r") as f:
                user_onion = f.read().strip()
                return user_onion     
        await asyncio.sleep(0.2)
    return