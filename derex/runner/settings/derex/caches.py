CACHES = {
    "default": {
        "KEY_PREFIX": "default",
        "VERSION": "1",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "derex_django.memcache.safe_key",
        "LOCATION": "memcached:11211",
    },
    "general": {
        "KEY_PREFIX": "general",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "derex_django.memcache.safe_key",
        "LOCATION": "memcached:11211",
    },
    "mongo_metadata_inheritance": {
        "KEY_PREFIX": "mongo_metadata_inheritance",
        "TIMEOUT": 300,
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "derex_django.memcache.safe_key",
        "LOCATION": "memcached:11211",
    },
    "staticfiles": {
        "KEY_PREFIX": "staticfiles_lms",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "derex_django.memcache.safe_key",
        "LOCATION": "memcached:11211",
    },
    "configuration": {
        "KEY_PREFIX": "configuration",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "derex_django.memcache.safe_key",
        "LOCATION": "memcached:11211",
    },
    "celery": {
        "KEY_PREFIX": "celery",
        "TIMEOUT": "7200",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "derex_django.memcache.safe_key",
        "LOCATION": "memcached:11211",
    },
    "course_structure_cache": {
        "KEY_PREFIX": "course_structure",
        "TIMEOUT": "7200",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "derex_django.memcache.safe_key",
        "LOCATION": "memcached:11211",
    },
    "ora2-storage": {
        "KEY_PREFIX": "ora2-storage",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "derex_django.memcache.safe_key",
        "LOCATION": "memcached:11211",
    },
}
