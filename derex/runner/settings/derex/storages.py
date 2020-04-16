DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"

AWS_ACCESS_KEY_ID = "minio_derex"
AWS_SECRET_ACCESS_KEY = "derex_default_secret"
AWS_S3_ENDPOINT_URL = "http://minio:4500/"

AWS_S3_CALLING_FORMAT = "boto.s3.connection.OrdinaryCallingFormat"
AWS_S3_HOST = "minio"
AWS_S3_PORT = 4500
AWS_S3_USE_SSL = False
AWS_QUERYSTRING_AUTH = False
S3_USE_SIGV4 = True

COURSE_IMPORT_EXPORT_STORAGE = DEFAULT_FILE_STORAGE
USER_TASKS_ARTIFACT_STORAGE = DEFAULT_FILE_STORAGE


# Bucket names: they need to be kept in sync with project.py
AWS_STORAGE_BUCKET_NAME = DEREX_PROJECT + "-main"
FILE_UPLOAD_STORAGE_BUCKET_NAME = DEREX_PROJECT + "-file-upload"
COURSE_IMPORT_EXPORT_BUCKET = DEREX_PROJECT + "-course-import-export"
GRADES_BUCKET_NAME = DEREX_PROJECT + "-grades-download"
FINANCIAL_REPORTS_BUCKET_NAME = DEREX_PROJECT + "-financial-reports"

FILE_UPLOAD_STORAGE_PREFIX = "submissions_attachments"

GRADES_DOWNLOAD = {
    "STORAGE_CLASS": DEFAULT_FILE_STORAGE,
    "STORAGE_KWARGS": {
        "bucket": GRADES_BUCKET_NAME,
        "ROOT_PATH": "/tmp/edx-s3/grades",
        "STORAGE_TYPE": "localfs",
    },
    "STORAGE_TYPE": "",
    "BUCKET": None,
    "ROOT_PATH": None,
}

FINANCIAL_REPORTS = {
    "BUCKET": FINANCIAL_REPORTS_BUCKET_NAME,
    "ROOT_PATH": "/tmp/edx-s3/reports",
    "STORAGE_TYPE": "localfs",
}

# This is needed for the Sysadmin dashboard "Git Logs" tab
GIT_REPO_DIR = os.path.join(MEDIA_ROOT, "course_repos")
