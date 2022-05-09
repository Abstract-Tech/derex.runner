# This module host settings which needs to be defined even if
# not used

CMS_SEGMENT_KEY = None

# enterprise.views tries to access settings.ECOMMERCE_PUBLIC_URL_ROOT,
ECOMMERCE_PUBLIC_URL_ROOT = None

# This needs to be defined even if Xqueue is not needed
XQUEUE_INTERFACE = {"url": None, "django_auth": None}

# Certifacates need this
FACEBOOK_APP_ID = None

# The common.py file includes the statements
# CREDENTIALS_INTERNAL_SERVICE_URL = None
# CREDENTIALS_PUBLIC_SERVICE_URL = None
# But for some reason if we import the code the values are different:
# >>> from lms.envs import common
# >>> common.CREDENTIALS_PUBLIC_SERVICE_URL, common.CREDENTIALS_INTERNAL_SERVICE_URL
# ('http://localhost:8008', 'http://localhost:8008')
CREDENTIALS_INTERNAL_SERVICE_URL = None
CREDENTIALS_PUBLIC_SERVICE_URL = None
