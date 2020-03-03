#!/bin/sh
set -e

if [ \! -f /root/.transifexrc ]; then
    echo "Transifex credentials unset. Building without translations."
    exit 0
fi

set -x

cd /openedx/edx-platform

i18n_tool transifex pull
i18n_tool extract

i18n_tool generate

python manage.py lms --settings=derex.assets compilemessages -v2
python manage.py cms --settings=derex.assets compilemessages -v2

python manage.py lms --settings=derex.assets compilejsi18n -v2
python manage.py cms --settings=derex.assets compilejsi18n -v2

i18n_tool validate || (find conf|grep prob; find conf|grep prob|xargs cat; false)

rm ~/.transifexrc
