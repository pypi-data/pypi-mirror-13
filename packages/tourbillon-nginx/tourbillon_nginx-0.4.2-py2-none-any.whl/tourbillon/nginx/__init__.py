import sys

PY34_PLUS = sys.version_info[0] == 3 and sys.version_info[1] >= 4

if PY34_PLUS:
    from .nginx.nginx import get_nginx_stats
else:
    from .nginx2.nginx import get_nginx_stats
