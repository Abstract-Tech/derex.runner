#!/bin/sh
set -ex

export PATH=/openedx/edx-platform/node_modules/.bin:/openedx/bin:${PATH}
export NO_PREREQ_INSTALL=True
export NO_PYTHON_UNINSTALL=True
export DJANGO_SETTINGS_MODULE="derex_django.settings.build.assets"

cd /openedx/edx-platform
SERVICE_VARIANT="lms" python manage.py lms collectstatic --noinput \
    --ignore "fixtures" \
    --ignore "karma_*.js" \
    --ignore "spec" \
    --ignore "spec_helpers" \
    --ignore "spec-helpers" \
    --ignore "xmodule_js" \
    --ignore "geoip" \
    --ignore "sass"

SERVICE_VARIANT="cms" python manage.py cms collectstatic --noinput \
    --ignore "fixtures" \
    --ignore "karma_*.js" \
    --ignore "spec" \
    --ignore "spec_helpers" \
    --ignore "spec-helpers" \
    --ignore "xmodule_js" \
    --ignore "geoip" \
    --ignore "sass"
