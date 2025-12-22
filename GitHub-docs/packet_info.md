# RelayX Packet info
*This file aims to inform the user about packet information and all the metadata which is sent during file/msg/data transfer when using RelayX Messenger.*

## Packets :
#### These are all the packets used / mentioned.
- 1. HANDSHAKE_INIT
- 2. HANDSHAKE_RESP
- 3. msg
- 4. ack
- 5. FILE_TRANSFER_INIT
- 6. FILE_CHUNK
- 7. FILE_ACK

# Packet wise breakdown

### 1. HANDSHAKE_INIT
This is for sending / initiating a handshake.
```
{
    "type": "HANDSHAKE_INIT",
    "from": user_onion,
    "pub" : b64_encode(public_bytes),
    "nonce": b64_encode(nonce_a),
    "ts" : int(time.time())
}
```
- "type" is to distinguish between packets
- "from" is the sender's Onion address. Required for responses
- "pub" public bytes of an ephemeral X25519 key. Freshly generated every handshake 
- "nonce" is generated randomly. 16 bytes long. Used for a Diffie-Hellman handshake
- "ts" stands for timestamp

### 2. HANDSHAKE_RESP
This is for responding to an incoming handshake.
```
{
    "type": "HANDSHAKE_RESP",
    "from": user_onion,
    "pub" : b64_encode(public_bytes),
    "nonce_reply": nonce_a_b64,
    "nonce_b": b64_encode(nonce_b),
    "ts" : int(time.time())
}
```
### 3. Message
This is the message envelope sent to your contacts.
```
{
    "route": route.copy(),
    "msg_id" : msg_uuid,
    "payload": message,
    "from": user_onion,
    "to": recipient_onion,
    "stap": time.time(),
    "type": "msg"
}
```
- "route" consists of [user onion] + [route relays (1)] + [recipient onion]
- msg_id is a randomly generated UUID (uuid4) for deduplication in the db
- "payload" consists of the encrypted message
- "to" is the recipient's onion address
- "stap" stands for timestamp

### 4. ACK
This is the Acknowledgement sent to the sender when a message is received.
```
{
    "type" : "ack_resp",
    "msg_id": envelope.get("msg_id"),
    "from": user_onion,
    "to": envelope.get("from"),
    "stap": envelope.get("stap"),
    "is_ack": True,
}
```
- "is_ack" is used to determine whether to drop the message or not

### 5. FILE_TRANSFER_INIT
Provides data to the recipient about an incoming transfer and initializes a tmp file and a status file (shows progress).
```
{
    "type": "FILE_TRANSFER_INIT",
    "msg_id" : msg_id,
    "from": user_onion,
    "total_chunks" : total_chunks,
    "filename" : filename,
    "ts" : int(time.time())
}
```
- "total_chunks" are the number of chunks the file was split into. Required for initial truncation
- "filename" is the name of the file. It is encrypted

### 6. FILE_CHUNK
This is the actual file chunk envelope.
```
{
    "type" : "FILE_CHUNK",
    "from" : user_onion,
    "to" : target_onion,
    "msg_id" : msg_id,
    "chunk_index" : chunk_index,
    "data" : chunk_data
}
```
- "chunk_index" is the index of the chunk, ie; 98th chunk would have index 97. Makes it easier to send and write to disk on the recipient's side
- "data" is the encrypted chunk data in bytes.

### 7. FILE_ACK
Collective acks to stop the resending of the same chunks
```
{
    "type" : "FILE_ACK",
    "msg_id": msg_id,
    "acked_upto" : new_acked_upto,
    "from": user_onion,
    "to": sender_onion,
}
```
- "acked_upto" provides the sender the collective chunk indices to stop sending those chunks which have been acked. Prevents Tor from congesting and also reduces client sided overhead