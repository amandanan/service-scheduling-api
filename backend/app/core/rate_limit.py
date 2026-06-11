from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter, keyed by client IP. Used to throttle the public,
# unauthenticated booking endpoints against spam / abuse.
limiter = Limiter(key_func=get_remote_address)
