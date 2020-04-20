Autocompletion
==============

Install
-------

To enable bash autocompletion run::

   _DEREX_COMPLETE=source derex | sudo tee /etc/bash_completion.d/derex
    for WRAPPED_SCRIPT in project services; do
        curl -s -L https://raw.githubusercontent.com/docker/compose/1.25.4/contrib/completion/bash/docker-compose \
        | sed -E "s/docker([-_])compose/ddc\1${WRAPPED_SCRIPT}/g;" \
        | sudo tee /etc/bash_completion.d/ddc-${WRAPPED_SCRIPT} > /dev/null
    done

This will enable it for all future shells. To also enable completion in the current shell run::

    eval "$(cat /etc/bash_completion.d/derex)"
    eval "$(cat /etc/bash_completion.d/ddc-project)"
    eval "$(cat /etc/bash_completion.d/ddc-services)"
