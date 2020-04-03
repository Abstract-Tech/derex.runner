from openedx.core.storage import ProductionStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage


class WhitenoiseEdxStorage(CompressedManifestStaticFilesStorage, ProductionStorage):
    def stored_name(self, name):
        try:
            return super(WhitenoiseEdxStorage, self).stored_name(name)
        except ValueError:
            return ProductionStorage.stored_name(self, name)
