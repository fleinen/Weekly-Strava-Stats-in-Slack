from pathlib import Path
from appdirs import user_data_dir


def get_app_data_dir() -> Path:
    """
    Get the application data directory for the 'strava-slack-integration' app.

    Returns:
        Path: The path to the application data directory.
    """
    app_data_dir = Path(user_data_dir('strava-slack-integration', 'tum-sse'))
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir
