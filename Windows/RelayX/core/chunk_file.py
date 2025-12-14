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
        "from" : user_onion,
        "to" : target_onion,
        "msg_id" : msg_id,
        "chunk_index" : chunk_index,
        "data" : chunk_data
    }
    await send_via_tor(target_onion, LISTEN_PORT, packet, PROXY)


async def _send_loop(msg_id: str):
    while True:
        async with pending_lock:
            t = config.pending_transfers.get(msg_id) # t because im lazy
            if not t:
                return
            
            inflight = t["next_idx"] - t["last_acked"]
            if inflight >= t["window"]:
                pass
            else:
                idx = t["next_idx"]
                if idx <t["total_chunks"]:
                    data = t["chunks"].get(idx)
                    t["next_idx"] += 1
                else:
                    data = None
        
        if data is not None:
            await send_chunk_process(idx, data, t["to"], msg_id)
        else:
            await asyncio.sleep(0.01)


async def send_file(chunks : dict , target_onion : str, filename : str):
    """
    chunks : {index : bytes}
    """

    msg_id = str(uuid.uuid4())
    total_chunks = len(chunks)
    #key = session_key[target_onion]
    #if not key:
        #print(f"[FILE_SEND_ERROR] Cannot send {filename}.\nNo Session key exists for {target_onion}")
        #return
    
    #encrypted_chunks = encrypt_chunks(chunks, key)
    
    async with pending_lock:
        config.pending_transfers[msg_id] = {
            "to" : target_onion,
            "chunks" : chunks.copy(),
            "next_idx" : 0,
            "last_acked" : -1,
            "window" : 16,
            "total_chunks" : total_chunks,
            "ts" : int(time.time())
        }

    # Details so the recipient can join chunks
    metadata_packet = file_init_metadata(total_chunks, filename, msg_id)
    await send_via_tor(target_onion, LISTEN_PORT, metadata_packet, PROXY)
    asyncio.create_task(_send_loop(msg_id))