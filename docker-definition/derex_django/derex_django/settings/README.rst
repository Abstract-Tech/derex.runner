Settings for edX
================

This directory contains django settings files that `derex.runner` uses to drive
edX. If your project does not have a `settings` directory, this one will be
used for you, and its `default/base.py` file will be used to configure the LMS and CMS.

If your project has a `settings` directory and `materialize_derex_settings` is true
in your project `derex.config.yaml` (that's the default behavior), it will be populated
using these files. The files derex copies to your project dir are not meant to be edited.
If you upgrade derex, a new version of these files might be bundled. In this
case the existing files in the project will be updated to the new content.
