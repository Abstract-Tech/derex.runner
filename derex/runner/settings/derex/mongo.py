try:
    from pathlib import Path
except ImportError:
    from path import Path

from xmodule.modulestore.modulestore_settings import update_module_store_settings


DATA_DIR = Path("/openedx/data")

MONGODB_HOST = "mongodb"
MONGODB_DB_NAME = os.environ["MONGODB_DB_NAME"]
DOC_STORE_CONFIG = {
    "host": MONGODB_HOST,
    "db": MONGODB_DB_NAME,
    "user": os.environ["MONGODB_USER"],
    "password": os.environ["MONGODB_PASSWORD"],
    "authsource": "admin",
}
CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "DOC_STORE_CONFIG": DOC_STORE_CONFIG,
}
update_module_store_settings(
    MODULESTORE,
    doc_store_settings=DOC_STORE_CONFIG,
    module_store_options={"fs_root": DATA_DIR},
)

# This is needed for the Sysadmin dashboard "Git Logs" tab
MONGODB_LOG = {
    "host": DOC_STORE_CONFIG["host"],
    "db": "{}_xlog".format(MONGODB_DB_NAME),
    "user": DOC_STORE_CONFIG["user"],
    "password": DOC_STORE_CONFIG["password"],
}
