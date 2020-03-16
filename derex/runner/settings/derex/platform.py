PLATFORM_NAME = "TestEdX"

LMS_BASE = "http://localhost:4700"
CMS_BASE = "http://localhost:4800"

# Provide a default for SITE_NAME
# It will be overridden later, if an `lms_site_name` variable has been specified in the config
SITE_NAME = {"lms": "localhost:4700", "cms": "localhost:4700"}[SERVICE_VARIANT]

if SERVICE_VARIANT == "cms":
    CMS_SEGMENT_KEY = "foobar"
    LOGIN_URL = "/signin"
    FRONTEND_LOGIN_URL = LOGIN_URL
