

import os

import django

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]
ROOT_URLCONF = "%s.urls" % PROJECT_DIRNAME

try:
    import django.test.runner
    TEST_RUNNER = "django.test.runner.DiscoverRunner"
except ImportError as e:
    TEST_RUNNER = "django.test.simple.DjangoTestSuiteRunner"

SECRET_KEY = "hi mom"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.db',
    }
}

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates"),)

TEMPLATE_OPTIONS = {}
if django.VERSION >= (1, 9):
    # only set builtins option on Django >= 1.9
    TEMPLATE_OPTIONS = {
        'builtins': ['overextends.templatetags.overextends_tags'],
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': TEMPLATE_DIRS,
        'OPTIONS': TEMPLATE_OPTIONS
    },
]

INSTALLED_APPS = (
    'overextends',
)
