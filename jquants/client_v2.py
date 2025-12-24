"""J-Quants API V2 Client (Placeholder for Phase 2)."""

from typing import Optional


class ClientV2:
    """
    J-Quants API V2 Client

    This is a placeholder class for Phase 2 implementation.
    V2 API uses API key authentication instead of email/password.

    ref. https://jpx-jquants.com/ja/spec
    """

    JQUANTS_API_BASE = "https://api.jquants.com/v2"
    MAX_WORKERS = 5

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        rate_limit: Optional[int] = None,
    ) -> None:
        """
        Args:
            api_key: J-Quants API key (or set JQUANTS_API_KEY environment variable)
            rate_limit: Rate limit (req/min).
                        None (default): No limit, auto-retry on 429.
                        int: Throttle at specified value.
        """
        # Phase 2 implementation
        raise NotImplementedError(
            "ClientV2 is not yet implemented. "
            "This will be available in Phase 2. "
            "Please use ClientV1 for now."
        )
