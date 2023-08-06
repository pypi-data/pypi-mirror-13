from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    Elasticsearch runnable thread.

    Examples:

        You can just add it to your Django development settings with::

            IEVVTASKS_DEVELOPRUN_THREADLIST = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.elasticsearch.RunnableThread(
                        configpath='not_for_deploy/elasticsearch.develop.yml')
                )
            }

    """
    default_autorestart_on_crash = True

    def __init__(self, configpath, elasticsearch_executable='elasticsearch', **kwargs):
        self.configpath = configpath
        self.elasticsearch_executable = elasticsearch_executable
        super(RunnableThread, self).__init__(**kwargs)

    def get_logger_name(self):
        return 'ElasticSearch {}'.format(self.configpath)

    def get_command_config(self):
        return {
            'executable': self.elasticsearch_executable,
            'args': ['--config={}'.format(self.configpath)]
        }
