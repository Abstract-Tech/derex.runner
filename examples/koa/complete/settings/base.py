from derex_django.settings.default import *  # noqa: F401, F403


# Id of the site fixture to use, instead of looking up the hostname
SITE_ID = 1
LOGO_URL = "{}/static/demo-theme/images/logo.png".format(LMS_ROOT_URL)  # noqa: F405
LOGO_URL_PNG = LOGO_URL
