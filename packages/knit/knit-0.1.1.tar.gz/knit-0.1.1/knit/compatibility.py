from __future__ import absolute_import, division, print_function

import sys

if sys.version_info < (3,):
    FileNotFoundError = IOError
    PermissionError = IOError
    from urlparse import urlparse
else:
    PermissionError = PermissionError
    FileNotFoundError = FileNotFoundError
    from urllib.parse import urlparse
