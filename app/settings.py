import os

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, environment variables
    # must already be set by the shell or process manager
    pass


class Settings:
    """
    Minimal application settings.
    """
    def __init__(self):
        self.WHG_API_TOKEN = os.getenv("WHG_API_TOKEN")
        self.MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")   # public pk. token for the Sandbox terrain tiles
        self.EDOPS_VERSION_LABEL = os.getenv("EDOPS_VERSION_LABEL", "v1.0 alpha")   # the app version pill in every page header and on the splash
        self.EDOPS_SITE_MODE = os.getenv("EDOPS_SITE_MODE", "")                     # "v1alpha": the eyes-only v1 alpha (see app/site_mode.py); empty: as before
        self.EDOPS_LIVE_V04_URL = os.getenv("EDOPS_LIVE_V04_URL", "https://edops.computingplace.org")   # where the alpha points for v0.4
        self.EDOPS_ALPHA_DATE = os.getenv("EDOPS_ALPHA_DATE", "November 2026")      # the date shown in the alpha banner


settings = Settings()
