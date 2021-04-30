import json
import os


string_prefixes = ["DEREX_ALL_", "DEREX_{}_".format(SERVICE_VARIANT.upper())]
json_prefixes = ["DEREX_JSON_ALL_", "DEREX_JSON_{}_".format(SERVICE_VARIANT.upper())]


for key, value in os.environ.items():
    for prefix in string_prefixes:
        if key.startswith(prefix):
            varname = key[len(prefix) :]  # noqa: E203
            locals()[varname] = value

    for prefix in json_prefixes:
        if key.startswith(prefix):
            varname = key[len(prefix) :]  # noqa: E203
            locals()[varname] = json.loads(value)
