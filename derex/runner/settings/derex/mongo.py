from xmodule.modulestore.modulestore_settings import update_module_store_settings


MONGODB_HOST = "mongodb"
MONGODB_DB = os.environ.get("MONGO_DB", "mongoedx")
CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "DOC_STORE_CONFIG": {"host": MONGODB_HOST, "db": MONGODB_DB},
}
DOC_STORE_CONFIG = {"host": MONGODB_HOST, "db": MONGODB_DB}
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)

if DEREX_PROJECT:
    # Mongodb
    MONGODB_DB = "{}_mongoedx".format(DEREX_PROJECT)
    DOC_STORE_CONFIG["db"] = MONGODB_DB
    CONTENTSTORE["DOC_STORE_CONFIG"] = DOC_STORE_CONFIG
    for store in MODULESTORE["default"]["OPTIONS"]["stores"]:
        store["DOC_STORE_CONFIG"]["db"] = MONGODB_DB
