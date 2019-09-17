from path import Path

import os
import sys


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]
assert SERVICE_VARIANT in ("lms", "cms")
exec("from {}.envs.derex.base import *".format(SERVICE_VARIANT), globals(), locals())


# Id of the site fixture to use, instead of looking up the hostname
SITE_ID = 1
