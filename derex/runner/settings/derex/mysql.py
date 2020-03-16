import os


MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
MYSQL_DB = os.environ.get("MYSQL_DB", "derex")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "secret")
DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": True,
        "ENGINE": "django.db.backends.mysql",
        "HOST": MYSQL_HOST,
        "NAME": MYSQL_DB,
        "PASSWORD": MYSQL_PASSWORD,
        "PORT": MYSQL_PORT,
        "USER": MYSQL_USER,
    }
}

if DEREX_PROJECT:
    MYSQL_DB = "{}_myedx".format(DEREX_PROJECT)
    DATABASES["default"]["NAME"] = MYSQL_DB
