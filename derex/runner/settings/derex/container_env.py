import os


SERVICE_VARIANT = os.environ["SERVICE_VARIANT"]

wildcard_prefix = "DEREX_" + "*" + "_"
prefix = "DEREX_" + SERVICE_VARIANT.upper() + "_"

for key, value in os.environ.items():
    if key.startswith(prefix):
        varname = key[len(prefix) :]  # noqa  This is the way black likes it
        locals()[varname] = value
    elif key.startswith(wildcard_prefix):
        varname = key[len(wildcard_prefix) :]  # noqa  This is the way black likes it
        locals()[varname] = value
