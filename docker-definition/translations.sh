#!/bin/sh
set -e

if [ \! -f /root/.transifexrc-orig ]; then
    echo "Transifex credentials unset. Building without translations."
    ls -la /root/
    exit 0
fi

set -x
# Unfortunately transifex really wants to rewrite its config file on every invocation.
# This behaviour can be tested with:
# python -c "import txclib.utils; txclib.utils.get_transifex_config(u'/root/.transifexrc')"
# https://github.com/transifex/transifex-client/issues/181
# To work around this we copy the file and remove the copy before exiting
cp /root/.transifexrc-orig /root/.transifexrc

cd /openedx/edx-platform

# Enable German translations
sed -i '/de_DE/ s/# -/-/' conf/locale/config.yaml
# Enable Italian translations
sed -i '/it_IT/ s/# -/-/' conf/locale/config.yaml

# The Basque translations has issues in Juniper (the only release where it's enabled so far)
sed -i '/eu_ES/d' conf/locale/config.yaml

i18n_tool transifex pull
i18n_tool extract

i18n_tool generate

python manage.py lms --settings=derex.assets compilemessages -v2
python manage.py cms --settings=derex.assets compilemessages -v2

python manage.py lms --settings=derex.assets compilejsi18n -v2
python manage.py cms --settings=derex.assets compilejsi18n -v2

# This check is currently done in the azure pipeline.
# i18n_tool validate || (find conf|grep prob; find conf|grep prob|xargs cat; false)

rm /root/.transifexrc
