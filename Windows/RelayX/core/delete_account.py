import os, shutil, asyncio, signal
from plyer import notification

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))

from RelayX.core.tor_bootstrap import stop_tor


async def shutdown_backend(delay : float = 0.5):
    await asyncio.sleep(delay)
    os.kill(os.getpid(), signal.SIGINT)

async def perform_account_deletion():
    try:
        stop_tor()
        db_file = os.path.join(PROJECT_ROOT, "RelayX", "database", "RelayX.db")
        with open(db_file, "w") as f:
            f.write("")
        data_dir = os.path.join(PROJECT_ROOT, "Networking", "data")
        shutil.rmtree(data_dir)
        asyncio.create_task(shutdown_backend())
    except Exception:
        notification.notify(title="RelayX Core : Account Deletion", message=f"Account Deletion was Unsuccessful. Please try again.", timeout=4)
        return 