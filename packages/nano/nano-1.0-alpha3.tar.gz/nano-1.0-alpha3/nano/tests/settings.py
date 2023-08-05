import django

SECRET_KEY = 'stuffandnonsense'

APPS = [
    'nano.activation',
    'nano.badge',
    'nano.blog',
    'nano.chunk',
    'nano.comments',
    'nano.countries',
    'nano.faq',
    'nano.link',
    'nano.mark',
    'nano.privmsg',
    'nano.tools',
    'nano.user',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
] + APPS

MIDDLEWARE_CLASSES = ()

if django.VERSION[:2] < (1, 6):
    INSTALLED_APPS += ['discover_runner']
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
