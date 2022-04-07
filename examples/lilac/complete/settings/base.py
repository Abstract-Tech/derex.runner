# flake8: noqa

from derex_django.settings.default import *


if DEREX_OPENEDX_VERSION == "lilac":
    FEATURES["ENABLE_ACCOUNT_MICROFRONTEND"] = True
    FEATURES["ENABLE_PROFILE_MICROFRONTEND"] = True

    ENABLE_PROFILE_MICROFRONTEND = True

    # The trailing slash here is needed or the URL will be joined with the
    # user username in an horrible way
    PROFILE_MICROFRONTEND_URL = "http://profile.lilac-minimal.localhost.derex"
    ACCOUNT_MICROFRONTEND_URL = "http://account.lilac-minimal.localhost.derex"
    WRITABLE_GRADEBOOK_URL = "http://gradebook.lilac-minimal.localhost.derex"
    LEARNING_MICROFRONTEND_URL = "http://learning.lilac-minimal.localhost.derex"

    FEATURES["ENABLE_THIRD_PARTY_AUTH"] = True
    FEATURES["ENABLE_CROSS_DOMAIN_CSRF_COOKIE"] = True

    CROSS_DOMAIN_CSRF_COOKIE_NAME = "csrftoken"
    CROSS_DOMAIN_CSRF_COOKIE_DOMAIN = ".localhost.derex"

    CORS_ORIGIN_WHITELIST = [
        LMS_BASE,
        CMS_BASE,
        PREVIEW_LMS_BASE,
        AWS_S3_ENDPOINT_URL,
        "account.lilac-minimal.localhost.derex",
        "profile.lilac-minimal.localhost.derex",
        "learning.lilac-minimal.localhost.derex",
        "gradebook.lilac-minimal.localhost.derex",
    ]

    LOGIN_REDIRECT_WHITELIST = [
        "account.lilac-minimal.localhost.derex",
        "profile.lilac-minimal.localhost.derex",
        "learning.lilac-minimal.localhost.derex",
        "gradebook.lilac-minimal.localhost.derex",
    ]
