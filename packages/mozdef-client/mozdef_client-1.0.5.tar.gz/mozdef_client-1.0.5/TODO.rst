TODO
----

- Could report to syslog when fire_and_forget_mode is True and we fail
- Could make requests threaded to emulate requests_futures, although its
  not as good
- Might want to limit event category to well-known default categories instead
  of a string (such as "authentication", "daemon", etc.)
- Might want to limit event severities to well-known default severities instead
  of a string (such as INFO, DEBUG, WARNING, CRITICAL, etc.)
- Might want to add documentation how to add your own CA certificate for this
  program to use
- It might be nice to move validation fields out of the functions to make
  updates easier (maybe in a configuration structure)
- Refactor into a "v2" for proper multi-destinations support (https vs sqs vs syslog vs..)
- RabbitMQ support
