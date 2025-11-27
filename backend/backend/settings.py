import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'constructos'),
        'USER': os.environ.get('POSTGRES_USER', 'constructos'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'constructos_dev_password'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),  # Docker Compose service name
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.environ.get('REDIS_HOST', 'redis')}:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
