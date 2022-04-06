# flake8: noqa

from derex_django.settings.default import *


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
    FEATURES["ENABLE_CROSS_DOMAIN_CSRF_COOKIE"] = True

    CROSS_DOMAIN_CSRF_COOKIE_NAME = "csrftoken"
    CROSS_DOMAIN_CSRF_COOKIE_DOMAIN = ".localhost"

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