import threading
import time


class DebateTimer:
    def __init__(self, seconds, on_finish=None):
        self.initial_time = seconds
        self.remaining = seconds
        self.on_finish = on_finish

        self._running = False
        self._paused = False
        self._lock = threading.Lock()
        self._thread = None

    def _run(self):
        while self._running and self.remaining > 0:
            time.sleep(1)
            with self._lock:
                if not self._paused:
                    self.remaining -= 1
                    print(f"Time left: {self.remaining}s")

        if self.remaining == 0 and self.on_finish:
            self.on_finish()

    def start(self):
        if not self._running:
            self._running = True
            self._paused = False
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def pause(self):
        with self._lock:
            self._paused = True

    def resume(self):
        with self._lock:
            self._paused = False

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()

    def reset(self, seconds=None):
        with self._lock:
            self.remaining = seconds if seconds is not None else self.initial_time