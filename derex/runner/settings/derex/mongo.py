from xmodule.modulestore.modulestore_settings import update_module_store_settings


MONGODB_HOST = "mongodb"
MONGODB_DB_NAME = os.environ["MONGODB_DB_NAME"]
CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "DOC_STORE_CONFIG": {"host": MONGODB_HOST, "db": MONGODB_DB_NAME},
}
DOC_STORE_CONFIG = {"host": MONGODB_HOST, "db": MONGODB_DB_NAME}
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

# This is needed for the Sysadmin dashboard "Git Logs" tab
MONGODB_LOG = {
    "host": DOC_STORE_CONFIG["host"],
    "db": "{}_xlog".format(MONGODB_DB_NAME),
}
