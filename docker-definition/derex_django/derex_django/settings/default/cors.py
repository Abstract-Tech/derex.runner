from corsheaders.defaults import default_headers as corsheaders_default_headers


FEATURES["ENABLE_CORS_HEADERS"] = True

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_INSECURE = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = corsheaders_default_headers + ("use-jwt-cookie",)
CORS_ORIGIN_WHITELIST = [
    LMS_BASE,
    CMS_BASE,
    PREVIEW_LMS_BASE,
    AWS_S3_ENDPOINT_URL,
]
