from watchdog.observers import Observer


class AsyncEventHandler(object):
    def __init__(self, loop=None, on_modified=None):
        self.on_modified = on_modified

    def dispatch(self, event):
        method_name = f"on_{event.event_type}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method(event)


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