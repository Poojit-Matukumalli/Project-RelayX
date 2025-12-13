import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.chunker.chunker import chunk_file
from RelayX.core.chunk_file import send_file

async def file_transfer(filepath, target_onion):
    filename = os.path.basename(filepath)

    chunks = chunk_file(filepath)
    if not chunks:
        print(f"[ERROR] Failed to chunk file : {filepath}")
        return
    
    await send_file(chunks, target_onion, filename)

