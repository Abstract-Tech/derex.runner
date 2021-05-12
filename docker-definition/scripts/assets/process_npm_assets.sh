#!/bin/sh
set -ex

export PATH=/openedx/edx-platform/node_modules/.bin:/openedx/bin:${PATH}
export NO_PREREQ_INSTALL=True
export NO_PYTHON_UNINSTALL=True
export DJANGO_SETTINGS_MODULE="derex_django.settings.build.assets"

cd /openedx/edx-platform
python -c "from pavelib.assets import process_npm_assets; process_npm_assets()"
