try:
    from pathlib import Path
except ImportError:
    from path import Path

from xmodule.modulestore.modulestore_settings import update_module_store_settings


MONGODB_HOST = "mongodb"
MONGODB_DB_NAME = os.environ["MONGODB_DB_NAME"]
DOC_STORE_CONFIG = {
    "host": MONGODB_HOST,
    "db": MONGODB_DB_NAME,
    "user": None,
    "password": None,
}
CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "DOC_STORE_CONFIG": DOC_STORE_CONFIG,
}
update_module_store_settings(
    MODULESTORE,
    doc_store_settings=DOC_STORE_CONFIG,
    module_store_options={"fs_root": Path("/openedx/data"),},
)

# This is needed for the Sysadmin dashboard "Git Logs" tab
MONGODB_LOG = {
    "host": DOC_STORE_CONFIG["host"],
    "db": "{}_xlog".format(MONGODB_DB_NAME),
}
