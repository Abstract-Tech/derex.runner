from openedx.core.storage import ProductionStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage


class WhitenoiseEdxStorage(CompressedManifestStaticFilesStorage, ProductionStorage):
    pass
