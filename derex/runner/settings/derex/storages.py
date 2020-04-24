DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

AWS_ACCESS_KEY_ID = "minio_derex"
AWS_SECRET_ACCESS_KEY = os.environ.get("DEREX_MINIO_SECRET")


AWS_S3_CALLING_FORMAT = "boto.s3.connection.OrdinaryCallingFormat"
AWS_S3_HOST = "minio.localhost"
AWS_S3_PORT = 80
AWS_S3_USE_SSL = False
AWS_QUERYSTRING_AUTH = True
S3_USE_SIGV4 = True
ORA2_FILEUPLOAD_BACKEND = "s3"

# Hack lifted from tutor-minio
# Configuring boto is required for ora2 because ora2 does not read
# host/port/ssl settings from django. Hence this hack.
# http://docs.pythonboto.org/en/latest/boto_config_tut.html
import os


os.environ["AWS_CREDENTIAL_FILE"] = "/tmp/boto.cfg"
with open("/tmp/boto.cfg", "w") as f:
    f.write(
        """[Boto]
is_secure = False
[s3]
host = {}
calling_format = boto.s3.connection.OrdinaryCallingFormat""".format(
            AWS_S3_HOST
        )
    )

COURSE_IMPORT_EXPORT_STORAGE = DEFAULT_FILE_STORAGE
USER_TASKS_ARTIFACT_STORAGE = DEFAULT_FILE_STORAGE


# Bucket names: they need to be kept in sync with project.py
FILE_UPLOAD_STORAGE_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME = DEREX_PROJECT

FILE_UPLOAD_STORAGE_PREFIX = "submissions_attachments"

GRADES_DOWNLOAD = {
    "STORAGE_CLASS": DEFAULT_FILE_STORAGE,
    "STORAGE_KWARGS": {
        "bucket": AWS_STORAGE_BUCKET_NAME,
        "ROOT_PATH": "/grades",
        "STORAGE_TYPE": "s3",
    },
}

FINANCIAL_REPORTS = {
    "BUCKET": AWS_STORAGE_BUCKET_NAME,
    "STORAGE_KWARGS": {
        "bucket": AWS_STORAGE_BUCKET_NAME,
        "ROOT_PATH": "/reports",
        "STORAGE_TYPE": "s3",
    },
}

# This is needed for the Sysadmin dashboard "Git Logs" tab
GIT_REPO_DIR = os.path.join(MEDIA_ROOT, "course_repos")

# Media

MEDIA_ROOT = "http://minio.localhost/{}/openedx/media".format(AWS_STORAGE_BUCKET_NAME)
VIDEO_TRANSCRIPTS_SETTINGS.update(
    {
        "STORAGE_CLASS": DEFAULT_FILE_STORAGE,
        "STORAGE_KWARGS": {
            "bucket": AWS_STORAGE_BUCKET_NAME,
            "ROOT_PATH": "/video-transcripts",
            "STORAGE_TYPE": "s3",
            "base_url": "not-used-but-need-to-define",
            "location": "not-used-but-need-to-define",
        },
    }
)
VIDEO_IMAGE_SETTINGS.update(
    {
        "STORAGE_CLASS": DEFAULT_FILE_STORAGE,
        "STORAGE_KWARGS": {
            "bucket": AWS_STORAGE_BUCKET_NAME,
            "ROOT_PATH": "/video-images",
            "STORAGE_TYPE": "s3",
            "base_url": "not-used-but-need-to-define",
            "location": "not-used-but-need-to-define",
        },
    }
)

PROFILE_IMAGE_BACKEND.update(
    {
        "class": DEFAULT_FILE_STORAGE,
        "options": {
            "location": "/profile-images",
            "base_url": "not-used-but-need-to-define",
            "querystring_auth": False,
        },
        "STORAGE_KWARGS": {
            "bucket": AWS_STORAGE_BUCKET_NAME,
            "ROOT_PATH": "/profile-images",
            "STORAGE_TYPE": "s3",
        },
    }
)

if DEBUG:
    """Here we should make sure that the above settings don't break lms.urls
    """
