from collections.abc import Callable

from app.config import settings
from app.integrations.github_client import GitHubClient

GitHubFactory = Callable[[], GitHubClient]


def get_github_factory() -> GitHubFactory:
    """FastAPI dependency. Tests override this to inject a fake GitHub transport."""
    return lambda: GitHubClient(settings.github_token, settings.github_api_url)
