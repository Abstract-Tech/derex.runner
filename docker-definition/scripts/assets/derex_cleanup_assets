#!/bin/sh
set -ex

# Avoid dulicates: rmlint finds files with the same conents, keeps the oldest
# and symlinks the other copies. Do not mess with node_modules, or it will stop working.
# Also, it comes from a previous layer so there would be no space saved from symlinking it
# See https://rmlint.readthedocs.io/en/latest/tutorial.html#flagging-original-directories
# for more info
rmlint -o sh:rmlint.sh -c sh:symlink -o json:stderr -g \
    /openedx/staticfiles // /openedx/edx-platform/common/static \
    2>/dev/null
# Do not remove empty files/directories
sed "/# empty /d" -i rmlint.sh
./rmlint.sh -d -q > /dev/null
