#!/bin/sh
set -ex

export PATH=/openedx/edx-platform/node_modules/.bin:/openedx/bin:${PATH}
export NO_PREREQ_INSTALL=True
export NO_PYTHON_UNINSTALL=True
export DJANGO_SETTINGS_MODULE="derex_django.settings.build.assets"

cd /openedx/edx-platform
SERVICE_VARIANT="lms" python manage.py lms compile_sass lms --theme-dirs /openedx/edx-platform/themes
SERVICE_VARIANT="cms" python manage.py cms compile_sass cms --theme-dirs /openedx/edx-platform/themes
