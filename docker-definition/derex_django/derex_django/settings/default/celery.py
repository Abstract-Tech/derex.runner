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
CELERY_RESULT_BACKEND = "cache+memcached://memcached:11211/"

CELERY_IMPORTS = locals().get("CELERY_IMPORTS", [])
# XXX for some reason celery is not registering the bookmarks app
CELERY_IMPORTS = list(maybe_list(CELERY_IMPORTS)) + [
    "openedx.core.djangoapps.bookmarks.tasks",
    "openedx.core.djangoapps.content.course_overviews.tasks",
]
if DEREX_OPENEDX_VERSION in ["koa", "lilac"]:
    INSTALLED_APPS.extend(["django_celery_beat"])
    CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
else:
    CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

CELERYBEAT_SCHEDULE = {}
CELERYBEAT_MAX_LOOP_INTERVAL = 300

if DEREX_OPENEDX_VERSION == "lilac":
    CELERY_ROUTES = "openedx.core.lib.celery.routers.route_task"
else:
    CELERY_ROUTES = "{}.celery.Router".format(SERVICE_VARIANT)

CELERY_QUEUES = {"openedx.lms.default": {}, "openedx.cms.default": {}}
CELERY_DEFAULT_EXCHANGE = "openedx.{}".format(SERVICE_VARIANT)
CELERY_DEFAULT_QUEUE = "{}.default".format(CELERY_DEFAULT_EXCHANGE)

HIGH_PRIORITY_QUEUE = CELERY_DEFAULT_QUEUE
DEFAULT_PRIORITY_QUEUE = CELERY_DEFAULT_QUEUE
HIGH_MEM_QUEUE = CELERY_DEFAULT_QUEUE
COURSEGRAPH_JOB_QUEUE = DEFAULT_PRIORITY_QUEUE
SCRAPE_YOUTUBE_THUMBNAILS_JOB_QUEUE = DEFAULT_PRIORITY_QUEUE
SOFTWARE_SECURE_VERIFICATION_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE
UPDATE_SEARCH_INDEX_JOB_QUEUE = DEFAULT_PRIORITY_QUEUE
VIDEO_TRANSCRIPT_MIGRATIONS_JOB_QUEUE = DEFAULT_PRIORITY_QUEUE

CELERY_DEFAULT_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE
ACE_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE
BULK_EMAIL_ROUTING_KEY = HIGH_PRIORITY_QUEUE
BULK_EMAIL_ROUTING_KEY_SMALL_JOBS = DEFAULT_PRIORITY_QUEUE
CREDENTIALS_GENERATION_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE
GRADES_DOWNLOAD_ROUTING_KEY = HIGH_MEM_QUEUE
POLICY_CHANGE_GRADES_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE
PROGRAM_CERTIFICATES_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE
RECALCULATE_GRADES_ROUTING_KEY = DEFAULT_PRIORITY_QUEUE

# Defines alternate environment tasks, as a dict of form { task_name: alternate_queue }
ALTERNATE_ENV_TASKS = {
    "completion_aggregator.tasks.update_aggregators": "lms",
    "openedx.core.djangoapps.content.block_structure.tasks.update_course_in_cache": "lms",
    "openedx.core.djangoapps.content.block_structure.tasks.update_course_in_cache_v2": "lms",
}

# Defines the task -> alternate worker queue to be used when routing.
EXPLICIT_QUEUES = {
    "lms.djangoapps.grades.tasks.compute_all_grades_for_course": {
        "queue": POLICY_CHANGE_GRADES_ROUTING_KEY
    },
    "cms.djangoapps.contentstore.tasks.update_search_index": {
        "queue": UPDATE_SEARCH_INDEX_JOB_QUEUE
    },
}
