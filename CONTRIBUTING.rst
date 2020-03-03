.. highlight:: console

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at
https://github.com/Abstract-Tech/derex.runner/issues.

Please provide a minimal derex project and instructions to trigger the bug.


Get Started!
------------

Ready to contribute? Here's how to set up `derex.runner` for
local development.

1. Fork the `derex.runner` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/derex.runner.git

3. Activate a virtualenv for this project (we recommend direnv) and install derex.runner there::

    $ cd derex.runner/
    $ direnv allow  # Or, alternatively, activate a pristine python>=3.6 virtualenv
    $ pip install -r requirements_dev.txt -e .
    $ python setup.py develop

4. Install git pre commit hooks::

    $ pre-commit install

5. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

6. When you're done making changes, check that all tests still pass::

    $ pytest -m "not slowtest"  # will run only the faster tests
    $ pytest -m "slowtest"  # will run only the slow tests

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Create an azure pipeline to run your tests and make sure you keep it green.

9. When everything is green submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

    $ bumpversion patch # possible: major / minor / patch
    $ git push
    $ git push --tags
