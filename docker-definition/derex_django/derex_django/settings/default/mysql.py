import os


DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": True,
        "ENGINE": "django.db.backends.mysql",
        "HOST": "mysql",
        "NAME": os.environ["MYSQL_DB_NAME"],
        "USER": os.environ["MYSQL_USER"],
        "PASSWORD": os.environ["MYSQL_PASSWORD"],
        "PORT": "3306",
    }
}

if DEREX_OPENEDX_VERSION == "lilac":
    DATABASES["default"]["HOST"] = "mysql57"
