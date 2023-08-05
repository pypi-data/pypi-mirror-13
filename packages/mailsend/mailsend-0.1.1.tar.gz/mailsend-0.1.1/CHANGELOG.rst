0.1.1 (released 2015-12-21)
---------------------------

- Fixes for compatibility with envparse-0.2

0.1 (released 2015-12-19)
-------------------------

- Forked from https://github.com/rconradharris/tinysmtp
- Added configuration via URL (eg ``Connection('smtp://user@example.org')``)
- Various bug fixes
- Added ``rewrite_to`` argument to Mail class constructor method. This causes
  all messages to be rewritten to the given address(es), and is
  expected to be used for development/testing.
- Added ``bcc`` argument to Mail class constructor method. This causes
  all messages to be bcc'd to the given address(es).
- Added ``suppress_send`` argument to the Mail class constructor. This
  causes messages to not be sent (but may be still accessed via
  ``Mail.subscribe``)
