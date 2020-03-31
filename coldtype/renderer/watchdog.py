import asyncio
from watchdog.observers import Observer


class AsyncEventHandler(object):
    def __init__(self, loop=None, on_modified=None):
        self.on_modified = on_modified
        
        self._loop = loop or asyncio.get_event_loop()
        if hasattr(asyncio, 'create_task'):
            self._ensure_future = asyncio.create_task
        else:
            self._ensure_future = asyncio.ensure_future

    def dispatch(self, event):
        method_name = f"on_{event.event_type}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            self._loop.call_soon_threadsafe(self._ensure_future, method(event))


class AsyncWatchdog(object):
    def __init__(self, path, recursive=True, on_modified=None):
        self._observer = Observer()
        evh = AsyncEventHandler(on_modified=on_modified)
        self._observer.schedule(evh, str(path), recursive)

    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()