import os


DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": True,
        "ENGINE": "django.db.backends.mysql",
        "HOST": "mysql",
        "NAME": os.environ["MYSQL_DB_NAME"],
        "PASSWORD": "secret",
        "PORT": "3306",
        "USER": "root",
    }
}
