import os


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
assert SERVICE_VARIANT in ("lms", "cms")

exec("from {}.envs.derex.base import *".format(SERVICE_VARIANT), globals(), locals())
