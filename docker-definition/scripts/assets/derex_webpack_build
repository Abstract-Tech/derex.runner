#!/bin/sh
set -ex

# Run a Webpack build
NODE_ENV="production" STATIC_ROOT_LMS="/openedx/staticfiles" STATIC_ROOT_CMS="/openedx/staticfiles/studio" $(npm bin)/webpack --config="webpack.prod.config.js"
