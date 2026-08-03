class AIModuleError(Exception):
    """Base exception for all errors in the AI module."""
    pass

class SummaryError(AIModuleError):
    """Exception raised when summary generation fails."""
    pass
