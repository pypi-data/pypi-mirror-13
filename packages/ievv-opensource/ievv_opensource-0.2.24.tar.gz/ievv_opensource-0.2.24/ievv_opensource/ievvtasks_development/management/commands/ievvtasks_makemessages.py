from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run makemessages for the languages specified in the ' \
           'IEVVTASKS_MAKEMESSAGES_LANGUAGE_CODES setting.'

    def __build_python_translations(self):
        ignore = getattr(settings, 'IEVVTASKS_MAKEMESSAGES_IGNORE', [
            'static/*'
        ])
        management.call_command('makemessages',
                                locale=settings.IEVVTASKS_MAKEMESSAGES_LANGUAGE_CODES,
                                ignore=ignore)

    def __build_javascript_translations(self):
        ignore = getattr(settings, 'IEVVTASKS_MAKEMESSAGES_JAVASCRIPT_IGNORE', [
            'node_modules/*',
            'bower_components/*'
            'not_for_deploy/*',
        ])
        management.call_command('makemessages',
                                domain='djangojs',
                                locale=settings.IEVVTASKS_MAKEMESSAGES_LANGUAGE_CODES,
                                ignore=ignore)

    def handle(self, *args, **options):
        self.__build_python_translations()
        if getattr(settings, 'IEVVTASKS_MAKEMESSAGES_BUILD_JAVASCRIPT_TRANSLATIONS', False):
            self.__build_javascript_translations()
