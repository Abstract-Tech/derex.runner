============
derex.runner
============


.. image:: https://dev.azure.com/abstract-technology/derex.runner/_apis/build/status/Abstract-Tech.derex.runner?branchName=master
        :target: https://dev.azure.com/abstract-technology/derex.runner/_build

Run Open edX docker images


Quickstart
----------

Make sure you have python 3.6 or later and docker installed.

Run the following commands: ::

    git clone git@github.com:Abstract-Tech/derex.runner.git
    cd derex.runner
    direnv allow
    pip install -r requirements.txt -e .
    cd tests/fixtures/minimal/
    ddc up -d  # Start mysql, mongodb, rabbitmq and admin tools
    derex reset-mailslurper  # Prime the mailslurper mysql database
    ddc-local reset-mysql  # Prime the mysql database
    ddc-local up -d  # Start LMS/CMS daemons and workers
    ddc-local compile-theme  # Compile theme sass files

Then head to one of the started services:

    * http://localhost:4700 LMS
    * http://localhost:4800 CMS
    * http://localhost:5555 Flower (monitor celery workers)
    * http://localhost:4300 Mailslurper (debug emails sent by the platform)
    * http://localhost:4400 Adminer (mysql administration tool)
    * http://localhost:9000 Portainer (docker administration tool)

You can login to the CMS and LMS using one of these users (the password is always ``secret``):

    * Username: ``user``, email ``user@example.com``
      Represents a student user.
    * Username: ``staff``, email ``staff@example.com``
      Represents a member of the teaching staff.
    * Username: ``superuser``, email ``superuser@example.com``
      Represents an administrator of Open edX. This user
      has full permissions inside the platform.

Development setup
-----------------

Make sure you have direnv installed and configured. Also, set up git pre commit hooks. ::

    direnv allow
    pip install pre-commit
    pre-commit install --install-hooks

Credits
-------

This work uses extensively parts of the `tutor <https://github.com/regisb/tutor>`_ project. Many thanks to Régis Behmo!

This package was created with `Cookiecutter
<https://github.com/audreyr/cookiecutter>`_ and the `cookiecutter-namespace-template
<https://github.com/veit/cookiecutter-namespace-template>`_ project template.
