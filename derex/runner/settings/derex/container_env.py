import json
import os


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]

string_prefixes = ["DEREX_ALL_", "DEREX_{}_".format(SERVICE_VARIANT.upper())]
json_prefixes = ["DEREX_JSON_ALL_", "DEREX_JSON_{}_".format(SERVICE_VARIANT.upper())]


for key, value in os.environ.items():
    for prefix in string_prefixes:
        if key.startswith(prefix):
            varname = key[len(prefix) :]  # noqa  This is the way black likes it
            locals()[varname] = value

    for prefix in json_prefixes:
        if key.startswith(prefix):
            varname = key[len(prefix) :]  # noqa  This is the way black likes it
            locals()[varname] = json.loads(value)
