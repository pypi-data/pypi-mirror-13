import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_RUNNER = "django.test.runner.DiscoverRunner"
SECRET_KEY = 'i%&(axb!!5yfg6kv$m*ytf9i-0)z-&1y-wkmv^oz#6l&$*+!v6'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
