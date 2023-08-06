import pytest


def pytest_configure():
    import django
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        SOUTH_TESTS_MIGRATE=False,
        SITE_ID=1,
        SECRET_KEY='not very secret in tests',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',

            'tests',
            'refreshtoken',
        ),
        PASSWORD_HASHERS=(
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ),
        SOUTH_DATABASE_ADAPTERS={'default': 'south.db.sqlite3'},
        REST_FRAMEWORK={
            'DEFAULT_PERMISSION_CLASSES': (
                'refreshtoken.permissions.IsOwnerOrAdmin',
            ),
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
            ),
        },
        JWT_AUTH={
            'JWT_ALLOW_REFRESH': True,
        },
    )

    django.setup()


@pytest.fixture
def alice(request, django_user_model):
    return django_user_model.objects.create_user(
        username=request.fixturename,
    )


@pytest.fixture
def refresh_token(request, alice):
    from refreshtoken.models import RefreshToken

    return RefreshToken.objects.create(
        app=request.fixturename,
        user=alice,
    )
