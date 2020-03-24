PLATFORM_NAME = "TestEdX"
SITE_NAME = {"lms": "lms.localhost:4700", "cms": "studio.localhost:4700"}[
    SERVICE_VARIANT
]

LMS_BASE = "lms.localhost:4700"
CMS_BASE = "studio.localhost:4800"

LMS_ROOT_URL = "//{}".format(LMS_BASE)

PREVIEW_LMS_BASE = "preview.localhost:4700"
FEATURES["PREVIEW_LMS_BASE"] = PREVIEW_LMS_BASE
PREVIEW_DOMAIN = FEATURES["PREVIEW_LMS_BASE"].split(":")[0]
HOSTNAME_MODULESTORE_DEFAULT_MAPPINGS = {PREVIEW_DOMAIN: "draft-preferred"}


if SERVICE_VARIANT == "cms":
    LOGIN_URL = "/signin"
    FRONTEND_LOGIN_URL = reverse_lazy("login_redirect_to_lms")
    FRONTEND_LOGOUT_URL = LMS_ROOT_URL + "/logout"
