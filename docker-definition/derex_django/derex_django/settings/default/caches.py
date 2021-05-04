"""Cache configuration.
Use memcached. If derex_django is available use its cache function.
If not use the one bundled with Open edX.
"""
try:
    import derex_django  # noqa: F401

    CACHES_KEY_FUNCTION = "derex_django.memcache.safe_key"
except ImportError:
    CACHES_KEY_FUNCTION = "util.memcache.safe_key"


CACHES = {
    "default": {
        "KEY_PREFIX": "default",
        "VERSION": "1",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": CACHES_KEY_FUNCTION,
        "LOCATION": "memcached:11211",
    },
    "general": {
        "KEY_PREFIX": "general",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": CACHES_KEY_FUNCTION,
        "LOCATION": "memcached:11211",
    },
    "mongo_metadata_inheritance": {
        "KEY_PREFIX": "mongo_metadata_inheritance",
        "TIMEOUT": 300,
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": CACHES_KEY_FUNCTION,
        "LOCATION": "memcached:11211",
    },
    "staticfiles": {
        "KEY_PREFIX": "staticfiles_lms",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": CACHES_KEY_FUNCTION,
        "LOCATION": "memcached:11211",
    },
    "configuration": {
        "KEY_PREFIX": "configuration",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": CACHES_KEY_FUNCTION,
        "LOCATION": "memcached:11211",
    },
    "celery": {
        "KEY_PREFIX": "celery",
        "TIMEOUT": "7200",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": CACHES_KEY_FUNCTION,
        "LOCATION": "memcached:11211",
    },
    "course_structure_cache": {
        "KEY_PREFIX": "course_structure",
        "TIMEOUT": "7200",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": CACHES_KEY_FUNCTION,
        "LOCATION": "memcached:11211",
    },
    "ora2-storage": {
        "KEY_PREFIX": "ora2-storage",
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": CACHES_KEY_FUNCTION,
        "LOCATION": "memcached:11211",
    },
}
