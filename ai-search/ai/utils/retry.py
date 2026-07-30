class RetryHandler:
    """Retry decorator for external API calls with exponential backoff."""

    @staticmethod
    def retry(max_attempts: int = 3, backoff: float = 2.0):
        """Decorator: retry a function on failure with exponential backoff."""
        pass
