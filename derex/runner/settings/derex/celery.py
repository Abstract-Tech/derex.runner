from kombu.utils.functional import maybe_list


CELERY_BROKER_VHOST = "{}_edxqueue".format(DEREX_PROJECT)

CELERY_BROKER_TRANSPORT = "amqp"
CELERY_BROKER_HOSTNAME = "rabbitmq"
CELERY_BROKER_USER = "guest"
CELERY_BROKER_PASSWORD = "guest"
BROKER_URL = "{0}://{1}:{2}@{3}/{4}".format(
    CELERY_BROKER_TRANSPORT,
    CELERY_BROKER_USER,
    CELERY_BROKER_PASSWORD,
    CELERY_BROKER_HOSTNAME,
    CELERY_BROKER_VHOST,
)
CELERY_MONGODB_BACKEND_SETTINGS = {
    "database": MONGODB_DB_NAME,
    "taskmeta_collection": "taskmeta_collection",
}
CELERY_RESULT_BACKEND = "mongodb://{}/".format(MONGODB_HOST)
CELERY_RESULT_DB_TABLENAMES = {"task": "celery_edx_task", "group": "celery_edx_group"}

CELERY_IMPORTS = locals().get("CELERY_IMPORTS", [])
# XXX for some reason celery is not registering the bookmarks app
CELERY_IMPORTS = list(maybe_list(CELERY_IMPORTS)) + [
    "openedx.core.djangoapps.bookmarks.tasks"
]
CELERYBEAT_SCHEDULE = {}

CELERY_QUEUES = {"lms.default": {}, "cms.default": {}}
CELERY_ROUTES = "{}.celery.Router".format(SERVICE_VARIANT)
CELERY_DEFAULT_QUEUE = "{}.default".format(SERVICE_VARIANT)
CELERY_DEFAULT_EXCHANGE = "default"

HIGH_PRIORITY_QUEUE = CELERY_DEFAULT_QUEUE
DEFAULT_PRIORITY_QUEUE = CELERY_DEFAULT_QUEUE
HIGH_MEM_QUEUE = CELERY_DEFAULT_QUEUE

CELERY_DEFAULT_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE

# Bulk Email
BULK_EMAIL_ROUTING_KEY = HIGH_PRIORITY_QUEUE
BULK_EMAIL_ROUTING_KEY_SMALL_JOBS = DEFAULT_PRIORITY_QUEUE

# Grade Downloads
# These keys are used for all of our asynchronous downloadable files, including
# the ones that contain information other than grades.
GRADES_DOWNLOAD_ROUTING_KEY = HIGH_MEM_QUEUE
POLICY_CHANGE_GRADES_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE
RECALCULATE_GRADES_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE

# Credentials Service
CREDENTIALS_GENERATION_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE
PROGRAM_CERTIFICATES_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE

# Ace Plugin (ace_common)
ACE_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE
