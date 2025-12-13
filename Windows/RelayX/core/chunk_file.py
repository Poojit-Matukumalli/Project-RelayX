import os, sys, base64, time, uuid, asyncio
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from utilities.network.Client_RelayX import send_via_tor
from utilities.encryptdecrypt.encrypt_message import encrypt_bytes
from RelayX.utils.config import session_key, PROXY, LISTEN_PORT, user_onion
from RelayX.utils import config
from RelayX.utils.queue import pending_lock

def file_init_metadata(total_chunks : int, filename : str, msg_id) -> dict:
    return {
        "type": "FILE_TRANSFER_INIT",
        "msg_id" : msg_id,
        "from": user_onion,
        "total_chunks" : total_chunks,
        "filename" : filename,
        "ts" : int(time.time())
    }


def _encrypt_chunk_helper(args : tuple[int, bytes, bytes]):
    """Returns chunk_index  (class int) and encrypted_byes (class bytes)"""
    chunk_index, chunk_bytes, session_key = args
    encrypted_bytes = encrypt_bytes(session_key, chunk_bytes)
    return chunk_index, encrypted_bytes

def encrypt_chunks(chunks : dict, session_key : bytes, processes:int = 4) -> dict:
    """Func for Parallel encryption of chunks"""
    with Pool(processes) as pool:
        results = pool.map(_encrypt_chunk_helper, [(i,b,session_key) for i, b in chunks.items()])
    return dict(results)


async def send_chunk_process(chunk_index, chunk_data, target_onion, msg_id):
    packet = {
        "type" : "FILE_CHUNK",
        "msg_id" : msg_id,
        "chunk_index" : chunk_index,
        "data" : base64.b64encode(chunk_data).decode("utf-8")
    }
    await send_via_tor(target_onion, LISTEN_PORT, packet, PROXY)

async def send_file(chunks : dict , target_onion : str, filename : str):
    """
    chunks : {index : bytes}
    """

    msg_id = str(uuid.uuid4())
    total_chunks = len(chunks)

    # Details so the recipient can join chunks
    metadata_packet = file_init_metadata(total_chunks, filename, msg_id)
    await send_via_tor(target_onion, LISTEN_PORT, metadata_packet, PROXY)

    key = session_key[target_onion]
    if not key:
        return
    
    encrypted_chunks = encrypt_chunks(chunks, key)

    async with pending_lock:
        config.pending_transfers[msg_id] = {
            "target" : target_onion,
            "chunks" : encrypted_chunks.copy(),
            "total" : len(encrypted_chunks),
            "retries" : 0,
            "ts" : int(time.time())
        }

    MAX_RETRIES = 5
    ACK_TIMEOUT = 2
    WINDOW = 16
    while msg_id in config.pending_transfers:
        state = config.pending_transfers[msg_id]
        async with pending_lock:
            if not state["chunks"]:
                del config.pending_transfers[msg_id]
                print("[FILE SEND COMPLETE]")
            return
        if state["retries"] >= MAX_RETRIES:
            print("[FILE SEND FAILED] Missing chunks :", list(state["chunks"].items()))
            del config.pending_transfers[msg_id]
            return
        
        window = list(state["chunks"].items())[:WINDOW]

    tasks = [
        asyncio.create_task(
            send_chunk_process(idx, data, target_onion, msg_id)
            ) for idx, data in window
        ]
    await asyncio.gather(*tasks)

    async with pending_lock:
        state["retries"] += 1
        await asyncio.sleep(ACK_TIMEOUT)