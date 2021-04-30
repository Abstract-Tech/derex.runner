#!/bin/sh
set -ex

cd /openedx/edx-platform
export PATH=/openedx/edx-platform/node_modules/.bin:/openedx/bin:${PATH}

export NO_PREREQ_INSTALL=True
export NO_PYTHON_UNINSTALL=True
# Make sure SERVICE_VARIANT is not set: if it is the command
# `./manage.my lms etc-etc`
# will leave it as is and not set it to the correct value
unset SERVICE_VARIANT
paver update_assets --settings derex_django.settings.build.assets
