from openedx.core.lib.derived import derive_settings
from path import Path as path
from xmodule.modulestore.modulestore_settings import update_module_store_settings

import os


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
assert SERVICE_VARIANT in ("lms", "cms")

exec("from {}.envs.common import *".format(SERVICE_VARIANT), globals(), locals())

ENV_ROOT = (path(os.environ["CONFIG_ROOT"]) / "..").normpath()
DATA_DIR = ENV_ROOT / "data"
LOG_DIR = "/openedx/data/logs"
SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
assert SERVICE_VARIANT in ("lms", "cms")

DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": True,
        "ENGINE": "django.db.backends.mysql",
        "HOST": "mysql",
        "NAME": "myedx",
        "PASSWORD": "secret",
        "PORT": "3306",
        "USER": "root",
    }
}

CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "DOC_STORE_CONFIG": {"host": "mongodb", "db": "mongoedx"},
}
DOC_STORE_CONFIG = {"host": "mongodb", "db": "mongoedx"}
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

XQUEUE_INTERFACE = {"url": None, "django_auth": None}
ALLOWED_HOSTS = ["*"]

derive_settings(__name__)
