import asyncio, subprocess, os

async def load_onion():
    addr_file = os.path.join("Windows", "Networking", "data", "HiddenService","hostname")
    network_service = os.path.join("Windows", "utilities" ,"network", "network_service.py")

    if not os.path.exists(addr_file):
        subprocess.Popen([f"python -u {network_service}"],
                creationflags= subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL         
        )
    for _ in range(50):
        if os.path.exists(addr_file):
            with open(addr_file, "r") as f:
                addr_user_onion = f.read()
                return addr_user_onion
        asyncio.sleep(0.2)
    return None
