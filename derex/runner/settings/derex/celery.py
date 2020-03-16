from kombu.utils.functional import maybe_list


CELERY_BROKER_VHOST = "/"
if DEREX_PROJECT:
    CELERY_BROKER_VHOST = "{}_edxqueue".format(DEREX_PROJECT)

CELERY_BROKER_TRANSPORT = os.environ.get("CELERY_BROKER_TRANSPORT", "amqp")
CELERY_BROKER_HOSTNAME = os.environ.get("CELERY_BROKER_HOSTNAME", "rabbitmq")
CELERY_BROKER_USER = os.environ.get("CELERY_BROKER_USER", "guest")
CELERY_BROKER_PASSWORD = os.environ.get("CELERY_BROKER_PASSWORD", "guest")
BROKER_URL = "{0}://{1}:{2}@{3}/{4}".format(
    CELERY_BROKER_TRANSPORT,
    CELERY_BROKER_USER,
    CELERY_BROKER_PASSWORD,
    CELERY_BROKER_HOSTNAME,
    CELERY_BROKER_VHOST,
)
CELERY_MONGODB_BACKEND_SETTINGS = {
    "database": MONGODB_DB,
    "taskmeta_collection": "taskmeta_collection",
}
CELERY_RESULT_BACKEND = "mongodb://{MONGODB_HOST}/".format(**locals())
CELERY_RESULT_DB_TABLENAMES = {"task": "celery_edx_task", "group": "celery_edx_group"}

CELERY_QUEUES = {"lms.default": {}, "cms.default": {}}
CELERY_ROUTES = "{}.celery.Router".format(SERVICE_VARIANT)
CELERY_DEFAULT_QUEUE = "{}.default".format(SERVICE_VARIANT)

CELERY_IMPORTS = locals().get("CELERY_IMPORTS", [])
# XXX for some reason celery is not registering the bookmarks app
CELERY_IMPORTS = list(maybe_list(CELERY_IMPORTS)) + [
    "openedx.core.djangoapps.bookmarks.tasks"
]
