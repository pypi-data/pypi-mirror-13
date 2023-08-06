import six
import sys
from functools import wraps

def retry(f):
    """
    A retry decorator that does exponential backoff when a retryable condition is detected.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        exc_info = None

        try:
            result = f(*args, **kwargs)
        except Exception as ex:
            exc_info = sys.exc_info()

        # Out of retries, re-raise the exception or return the response
        if exc_info:
            # Re-raise exception, preserving original stack trace
            six.reraise(*exc_info)
        return result

    return wrapper


## retry_on(ValueError)
## found_team = _with_retry(syn.getTeam, name)
