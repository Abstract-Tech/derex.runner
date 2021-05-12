#!/bin/sh
set -ex

# This will also set his own Django settings so we need to make sure
# no DJANGO_SETTINGS_MODULE environment variable is already defined
unset DJANGO_SETTINGS_MODULE
export PATH=/openedx/edx-platform/node_modules/.bin:/openedx/bin:${PATH}
export NO_PREREQ_INSTALL=True
export NO_PYTHON_UNINSTALL=True

cd /openedx/edx-platform
xmodule_assets common/static/xmodule
