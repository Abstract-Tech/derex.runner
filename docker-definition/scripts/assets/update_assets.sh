#!/bin/sh
set -ex

# We can't use 'paver update_assets' command since it will
# always try to load settings from modules relative to the
# lms or cms 'envs' folder.

./process_xmodule_assets.sh
./process_npm_assets.sh
./webpack.sh
./compile_sass.sh
./collect_assets.sh
