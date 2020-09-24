PLATFORM_NAME = "TestEdX"

LMS_BASE = DEREX_PROJECT + ".localhost"
CMS_BASE = "studio." + LMS_BASE

LMS_ROOT_URL = "//{}".format(LMS_BASE)
SITE_NAME = {"lms": LMS_BASE, "cms": CMS_BASE}[SERVICE_VARIANT]

PREVIEW_LMS_BASE = "preview.{}".format(LMS_BASE)
FEATURES["PREVIEW_LMS_BASE"] = PREVIEW_LMS_BASE
PREVIEW_DOMAIN = FEATURES["PREVIEW_LMS_BASE"].split(":")[0]
HOSTNAME_MODULESTORE_DEFAULT_MAPPINGS = {PREVIEW_DOMAIN: "draft-preferred"}

SESSION_COOKIE_DOMAIN = LMS_BASE

if SERVICE_VARIANT == "cms":
    LOGIN_URL = "/signin"
    FRONTEND_LOGIN_URL = reverse_lazy("login_redirect_to_lms")
    FRONTEND_LOGOUT_URL = LMS_ROOT_URL + "/logout"

# We prefer to change the default value
# https://files.edx.org/openedx-logos/edx-openedx-logo-tag.png
# to a local URL to make sure derex installations of Open edX are self-contained
FOOTER_OPENEDX_LOGO_IMAGE = "/static/images/openedx-logo-tag.png"

WIKI_ENABLED = True
