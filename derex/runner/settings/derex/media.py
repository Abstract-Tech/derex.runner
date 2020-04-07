MEDIA_ROOT = "/openedx/media"
VIDEO_TRANSCRIPTS_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT
VIDEO_IMAGE_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT
PROFILE_IMAGE_BACKEND["options"].update(
    {
        "base_url": os.path.join(MEDIA_URL, "profile-images/"),
        "location": os.path.join(MEDIA_ROOT, "profile-images/"),
    }
)
