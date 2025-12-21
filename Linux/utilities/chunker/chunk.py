"""                   Chunker.py
This is the raw chunker module that chunks and returns the chunk index and file content (images, not txt) in bytes.

"""

import ctypes
from ctypes import c_int, c_size_t, c_char_p, POINTER, Structure
import sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, "..", ".."))
SO_PATH = os.path.join(ROOT, "chunker.so")
sys.path.insert(0, PROJECT_ROOT)

class Chunk(Structure):
    _fields_ = [("index", c_int),
                ("data", ctypes.POINTER(ctypes.c_char)),
                ("len", c_size_t)]
os.chdir(PROJECT_ROOT)
lib = ctypes.CDLL(SO_PATH)

lib.chunk_file.restype = POINTER(Chunk)
lib.chunk_file.argtypes = [c_char_p, c_size_t, POINTER(c_int)]
lib.free_chunks.argtypes = [POINTER(Chunk), c_int]

def chunk_file(path, chunk_size=1048576):
    count = c_int()
    chunks_ptr = lib.chunk_file(path.encode(), chunk_size, ctypes.byref(count))
    if not chunks_ptr:
        return None
    
    result = {}
    for i in range(count.value):
        chunk = chunks_ptr[i]
        result[chunk.index] = bytes(chunk.data[:chunk.len])
    
    lib.free_chunks(chunks_ptr, count.value)
    return result