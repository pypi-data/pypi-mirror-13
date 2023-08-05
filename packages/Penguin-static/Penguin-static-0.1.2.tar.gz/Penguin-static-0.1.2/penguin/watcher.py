"""
This is the watcher module, watches html and markdown files for changes
and compiler them through the compiler module when there's a change
"""

import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from .compiler import Compiler
from .penguin import Penguin


# Custom handler for handling change events
class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.html", "*.md"]

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print ("Compiling file...", event.src_path)  # print now only for degug

        site = Penguin()

        # Compile the file that was modified, we are currently working within
        # 'site'

        filepath = []  # If a html file changes

        path = event.src_path

        filepath.append(path)
        Compiler().compileJinja(site, filepath)

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)


class Watcher:

    def __init__(self, site):
        observer = Observer()
        observer.schedule(MyHandler(), path=site.source)
        observer.start()

        print("Polling for changes...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
