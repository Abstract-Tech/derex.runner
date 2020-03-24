DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
COURSE_IMPORT_EXPORT_STORAGE = DEFAULT_FILE_STORAGE
USER_TASKS_ARTIFACT_STORAGE = DEFAULT_FILE_STORAGE

AWS_STORAGE_BUCKET_NAME = ""
FILE_UPLOAD_STORAGE_BUCKET_NAME = ""
COURSE_IMPORT_EXPORT_BUCKET = ""

FILE_UPLOAD_STORAGE_PREFIX = "submissions_attachments"

GRADES_DOWNLOAD = {
    "STORAGE_CLASS": DEFAULT_FILE_STORAGE,
    "STORAGE_KWARGS": {
        "base_url": os.path.join(MEDIA_URL, "grades"),
        "location": os.path.join(MEDIA_ROOT, "grades"),
    },
    "STORAGE_TYPE": "",
    "BUCKET": None,
    "ROOT_PATH": None,
}

FINANCIAL_REPORTS = {
    "BUCKET": None,
    "ROOT_PATH": os.path.join(MEDIA_ROOT, "reports"),
    "STORAGE_TYPE": "localfs",
}

# This is needed for the Sysadmin dashboard "Git Logs" tab
GIT_REPO_DIR = os.path.join(MEDIA_ROOT, "course_repos")
