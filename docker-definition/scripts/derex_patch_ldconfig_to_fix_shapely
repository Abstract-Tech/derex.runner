#!/bin/sh

cp /sbin/ldconfig /sbin/ldconfig.orig

# Variant of http://www.etalabs.net/sh_tricks.html, mimics GNU & bash echo.
# with the addition that one can use echo - "$var" to output the content
# of $var verbatim (followed by a newline) like in zsh (but echo - still
# outputs - unlike in zsh).

my_echo() (  # Lifted from https://unix.stackexchange.com/tags/echo/info to silence shellcheck
  fmt=%s end='\n' IFS=' '
  while [ $# -gt 1 ] ; do
    case "$1" in ([!-]*|-*[!neE]*) break;; esac # not a flag
    case "$1" in (*n*) end='';; esac # no newline
    case "$1" in (*e*) fmt=%b;; esac # interpret backslash escapes
    case "$1" in (*E*) fmt=%s;; esac # don't interpret backslashes
    shift
  done
  # shellcheck disable=SC2059
  printf "$fmt$end" "$*"
)

# shellcheck disable=SC2016
(my_echo -e '#!/bin/sh
if [ "$1" = "-p" ]; then
    # Hack to mimic GNU ldconfig s -p option, needed by ctypes, used by shapely
    echo "    libc.musl-x86_64.so.1 (libc6,x86-64) => /lib/libc.musl-x86_64.so.1"
    echo "    libgeos_c.so (libc6,x86-64) => /usr/lib/libgeos_c.so"
    exit 0
fi
' ; tail -n +2 /sbin/ldconfig.orig) > /sbin/ldconfig
