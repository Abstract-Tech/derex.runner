import os


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
assert SERVICE_VARIANT in ("lms", "cms")
exec("from {}.envs.derex.base import *".format(SERVICE_VARIANT), globals(), locals())

USE_I18N = True
# LANGUAGE_CODE = "de-de"

# Id of the site fixture to use, instead of looking up the hostname
SITE_ID = 1

# Notes settings
FEATURES["ENABLE_EDXNOTES"] = True  # type: ignore  # noqa
EDXNOTES_PUBLIC_API = "http://localhost:8120/api/v1"
EDXNOTES_INTERNAL_API = "http://notes:8120/api/v1"
