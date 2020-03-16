MEDIA_ROOT = "/openedx/media"
VIDEO_TRANSCRIPTS_SETTINGS["location"] = MEDIA_ROOT  # type: ignore  # noqa
VIDEO_IMAGE_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT  # type: ignore  # noqa
PROFILE_IMAGE_BACKEND["options"]["location"] = MEDIA_ROOT  # type: ignore  # noqa
