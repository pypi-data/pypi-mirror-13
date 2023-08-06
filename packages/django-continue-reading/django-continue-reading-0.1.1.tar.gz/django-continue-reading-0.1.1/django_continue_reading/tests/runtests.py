import sys, os
import django
import django.test.utils
from django.conf import settings
from django.test.utils import get_runner


if not settings.configured:
    settings.configure(
        SITE_ID=1,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'testdb.sqlite3',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.contenttypes',
            'django.contrib.sites',
            'django_continue_reading',
            'django_continue_reading.tests',
        ]
    )

if __name__ == "__main__":
    # export DJANGO_SETTINGS_MODULE="django_continue_reading.tests.test_settings"
    os.environ['DJANGO_SETTINGS_MODULE'] = 'django_continue_reading.tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["django_continue_reading.tests.tests"])
    sys.exit(bool(failures))
