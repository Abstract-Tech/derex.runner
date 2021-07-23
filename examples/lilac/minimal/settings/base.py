# flake8: noqa

from corsheaders.defaults import default_headers as corsheaders_default_headers
from derex_django.settings.default import *
from xmodule.modulestore.modulestore_settings import update_module_store_settings


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

if DEREX_OPENEDX_VERSION in ["koa", "lilac"]:
    INSTALLED_APPS.extend(["django_celery_beat"])
    CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
else:
    CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

if DEREX_OPENEDX_VERSION == "lilac":
    CELERY_ROUTES = "openedx.core.lib.celery.routers.route_task"
else:
    CELERY_ROUTES = "{}.celery.Router".format(SERVICE_VARIANT)

if DEREX_OPENEDX_VERSION == "lilac":
    FEATURES["ENABLE_ACCOUNT_MICROFRONTEND"] = True
    FEATURES["ENABLE_PROFILE_MICROFRONTEND"] = True

    ENABLE_PROFILE_MICROFRONTEND = True

    # The trailing slash here is needed or the URL will be joined with the
    # user username in an horrible way
    PROFILE_MICROFRONTEND_URL = "http://profile.lilac-minimal.localhost/"
    ACCOUNT_MICROFRONTEND_URL = "http://account.lilac-minimal.localhost"
    WRITABLE_GRADEBOOK_URL = "http://gradebook.lilac-minimal.localhost"
    LEARNING_MICROFRONTEND_URL = "http://learning.lilac-minimal.localhost"

    FEATURES["ENABLE_THIRD_PARTY_AUTH"] = True
    FEATURES["ENABLE_CORS_HEADERS"] = True
    # FEATURES["ENABLE_CROSS_DOMAIN_CSRF_COOKIE"] = True

    # CROSS_DOMAIN_CSRF_COOKIE_NAME = "csrftoken"
    # CROSS_DOMAIN_CSRF_COOKIE_DOMAIN = ".localhost"

    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ALLOW_INSECURE = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = corsheaders_default_headers + ("use-jwt-cookie",)
    CORS_ORIGIN_WHITELIST = [
        LMS_BASE,
        CMS_BASE,
        PREVIEW_LMS_BASE,
        AWS_S3_ENDPOINT_URL,
        "account.lilac-minimal.localhost",
        "profile.lilac-minimal.localhost",
        "learning.lilac-minimal.localhost",
        "gradebook.lilac-minimal.localhost",
    ]

    LOGIN_REDIRECT_WHITELIST = [
        "account.lilac-minimal.localhost",
        "profile.lilac-minimal.localhost",
        "learning.lilac-minimal.localhost",
        "gradebook.lilac-minimal.localhost",
    ]

    DOC_STORE_CONFIG = {
        "host": "mongodb4",
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

    if DEREX_OPENEDX_VERSION == "lilac":
        DATABASES["default"]["HOST"] = "mysql57"
        ELASTIC_SEARCH_CONFIG[0]["host"] = "elasticsearch7"
