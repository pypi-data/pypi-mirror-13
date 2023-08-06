It provides file operations like: list, download, upload, syncup, syncdown, etc.

The main purpose is to utilize Baidu Yun in Linux environments (e.g. Raspberry Pi)

For more information, please refer to https://github.com/houtianze/bypy

Version History:
~~~~~~~~~~~~~~~~

-  1.2.15: Fix a severe bug (accidental directory deletion) in
   ``download`` command intoduced in 1.2.14
-  1.2.14: Add in ``download`` command
-  1.2.13: Remove argcomplete; Improve encoding handling prompting
-  1.2.12: Add in (optional) argcomplete
-  1.2.11: Fix Exception in error dump introduced in 1.2.10
-  1.2.10: Handle (32, 'EPIPE'); Warn LOUDLY on encoding failures;
   Remove 'is\_revision'
-  1.2.9: Fix formatex() Syntax Error; Handle (110, 'ETIMEDOUT')
-  1.2.8: Fix a Syntax Error; Handle {'error\_code': 0, 'error\_msg':
   'no error'}
-  1.2.7: Fix Hash Cache JSON saving (need to using string for Hashes)
-  1.2.6: Fix Hash Cache JSON dumping (``Unicode`` again)
-  1.2.5: Add in offline (cloud) download; Fix stack printing
-  1.2.4: Fix command line parsing for Python 3 (``Unicode`` by default)
-  1.2.3: Fix GUI for Python 3
-  1.2.2: Fix division for Python 3
-  1.2.1: Make it ``universal`` (Python 2 & 3 compatible)
-  1.0.20: Initial release



