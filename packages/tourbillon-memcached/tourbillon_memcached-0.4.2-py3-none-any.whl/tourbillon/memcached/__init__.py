import sys

PY34_PLUS = sys.version_info[0] == 3 and sys.version_info[1] >= 4

if PY34_PLUS:
    from .memcached.memcached import get_memcached_stats
else:
    from .memcached2.memcached import get_memcached_stats
