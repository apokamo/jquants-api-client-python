# this version will be overwritten by poetry-dynamic-versioning
__version__ = "0.0.0"

from .client_v2 import ClientV2
from .exceptions import (
    JQuantsAPIError,
    JQuantsForbiddenError,
    JQuantsRateLimitError,
)
