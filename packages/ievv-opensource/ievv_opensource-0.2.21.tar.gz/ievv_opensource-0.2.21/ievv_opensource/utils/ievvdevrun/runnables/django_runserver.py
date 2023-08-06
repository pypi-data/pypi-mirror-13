import sys

from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    Django runserver runnable thread.

    Examples:

        You can just add it to your Django development settings with::

            IEVVTASKS_DEVELOPRUN_THREADLIST = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.django_runserver.RunnableThread()
                )
            }

        And you can make it not restart on crash with::

            IEVVTASKS_DEVELOPRUN_THREADLIST = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.django_runserver.RunnableThread(
                        autorestart_on_crash=False)
                )
            }

    """
    default_autorestart_on_crash = True

    def get_logger_name(self):
        return 'Django development server'

    def get_command_config(self):
        return {
            'executable': sys.executable,
            'args': ['manage.py', 'runserver']
        }
