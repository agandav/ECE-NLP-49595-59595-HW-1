from collections import deque
import threading
from . import speech_to_text_microsoft

_recognized_chunks = deque()
_lock = threading.Lock()

def on_recognized(text):
    with _lock:
        _recognized_chunks.append(text)
    print("Heard: {}".format(text))

def start():
    speech_to_text_microsoft.set_up(on_recognized)
    speech_to_text_microsoft.start()

def stop():
    speech_to_text_microsoft.stop()

def get_input():
    with _lock:
        if _recognized_chunks:
            return _recognized_chunks.popleft()
    return None


def clear_buffer():
    with _lock:
        _recognized_chunks.clear()
