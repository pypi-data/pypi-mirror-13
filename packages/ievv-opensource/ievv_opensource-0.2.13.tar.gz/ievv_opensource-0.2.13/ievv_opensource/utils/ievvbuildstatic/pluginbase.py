from watchdog.observers import Observer

from ievv_opensource.utils.ievvbuildstatic.watcher import EventHandler
from ievv_opensource.utils.logmixin import LogMixin


class Plugin(LogMixin):
    """
    Base class for all plugins in ``ievvbuildstatic``.
    """

    #: The name of the plugin.
    name = None

    def __init__(self):
        self.app = None

    def install(self):
        """
        Install any packages required for this plugin.

        Should use :meth:`ievv_opensource.utils.ievvbuild.config.App.get_installer`.

        Examples:

            Install an npm package::

                def install(self):
                    self.app.get_installer(NpmInstaller).install(
                        'somepackage')
                    self.app.get_installer(NpmInstaller).install(
                        'otherpackage', version='~1.0.0')
        """

    def run(self):
        """
        Run the plugin. Put the code executed by the plugin each time files
        change here.
        """
        pass

    def watch(self):
        """
        Start a watching thread and return the thread.

        You should not need to override this --- override
        :meth:`.get_watch_folders` and :meth:`.get_watch_regexes`
        instead.
        """
        watchfolders = self.get_watch_folders()
        if not watchfolders:
            return
        watchregexes = self.get_watch_regexes()
        event_handler = EventHandler(
            plugin=self,
            regexes=watchregexes
        )
        observer = Observer()
        for watchfolder in watchfolders:
            observer.schedule(event_handler, watchfolder, recursive=True)
        self.get_logger().info('Starting watcher for folders {!r} with regexes {!r}.'.format(
            watchfolders, watchregexes))
        observer.start()
        return observer

    def get_watch_regexes(self):
        """
        Get the regex used when watching for changes to files.

        Defaults to a regex matching any files.
        """
        return [r'^.*$']

    def get_watch_folders(self):
        """
        Get folders to watch for changes when using ``ievv buildstatic --watch``.

        Defaults to an empty list, which means that no watching thread is started
        for the plugin.

        The folder paths must be absolute, so in most cases you should
        use ``self.app.get_source_path()`` (see
        :meth:`ievv_opensource.utils.ievvbuildstatic.config.App#get_source_path`)
        to turn user provided relative folder names into absolute paths.
        """
        return []

    def get_logger_name(self):
        return '{}.{}'.format(self.app.get_logger_name(), self.name)
