Autocompletion
==============

Install
-------

Bash
####

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


Fish
####

To enable fish autocompletion run::

    echo 'eval (env _DEREX_COMPLETE=source-fish derex)' > ~/.config/fish/completions/derex.fish
    curl https://raw.githubusercontent.com/brgmnn/fish-docker-compose/master/completions/docker-compose.fish| sed -e 's/docker\(.\)compose/ddc\1services/g' > ~/.config/fish/completions/ddc-services.fish
    curl https://raw.githubusercontent.com/brgmnn/fish-docker-compose/master/completions/docker-compose.fish| sed -e 's/docker\(.\)compose/ddc\1project/g' > ~/.config/fish/completions/ddc-project.fish

This will enable it for all future shells. To also enable completion in the current shell run::

    . ~/.config/fish/completions/derex.fish
    . ~/.config/fish/completions/ddc-services.fish
    . ~/.config/fish/completions/ddc-project.fish
