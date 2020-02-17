Autocompletion
==============

Install
-------

To enable bash autocompletion run::

   _DEREX_COMPLETE=source derex| sudo tee /etc/bash_completion.d/derex
    curl -L \
    https://raw.githubusercontent.com/docker/compose/$(docker-compose --version|sed 's/.*version.//;s/, .*//')/contrib/completion/bash/docker-compose \
    | sed -e "s/docker_compose/ddc_project/g;s/docker-compose/ddc-project/g" \
    | sudo tee /etc/bash_completion.d/ddc_project

This will enable it for all future shells. To also enable completion in the current shell run::

    eval "$(cat  /etc/bash_completion.d/derex)"
    eval "$(cat  /etc/bash_completion.d/ddc_project)"
