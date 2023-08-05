import threading
from watchdog.events import RegexMatchingEventHandler


class EventHandler(RegexMatchingEventHandler):
    """
    Event handler for watchdog --- this is used by each watcher
    thread to react to changes in the filesystem.

    This is instantiated by :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.watch`
    to watch for changes in files matching
    :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.get_watch_regexes`
    in the folders specified in
    :meth:`ievv_opensource.utils.ievvbuildstatic.pluginbase.Plugin.get_watch_folders`.
    """
    def __init__(self, *args, **kwargs):
        self.plugin = kwargs.pop('plugin')
        self.runtimer = None
        self.is_running = False
        super(EventHandler, self).__init__(*args, **kwargs)

    def handle_plugin_run(self):
        if self.is_running:
            return
        self.is_running = True
        self.plugin.run()
        self.is_running = False

    def on_any_event(self, event):
        if self.runtimer:
            self.runtimer.cancel()
        self.runtimer = threading.Timer(0.5, self.handle_plugin_run)
        self.runtimer.start()
