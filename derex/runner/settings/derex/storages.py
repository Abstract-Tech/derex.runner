DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

AWS_ACCESS_KEY_ID = "minio_derex"
AWS_SECRET_ACCESS_KEY = "derex_default_secret"

AWS_S3_CALLING_FORMAT = "boto.s3.connection.OrdinaryCallingFormat"
AWS_S3_HOST = "minio"
AWS_S3_PORT = 80
AWS_S3_USE_SSL = False
AWS_QUERYSTRING_AUTH = False
S3_USE_SIGV4 = True

COURSE_IMPORT_EXPORT_STORAGE = DEFAULT_FILE_STORAGE
USER_TASKS_ARTIFACT_STORAGE = DEFAULT_FILE_STORAGE


# Bucket names: they need to be kept in sync with project.py
AWS_STORAGE_BUCKET_NAME = DEREX_PROJECT

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
