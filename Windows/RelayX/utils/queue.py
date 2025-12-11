import asyncio
incoming_queue = asyncio.Queue()
ack_queue = asyncio.Queue()
rotation_lock = asyncio.Lock()
rotation_started = False
state_queue = asyncio.Queue()