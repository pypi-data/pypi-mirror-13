README
======

``fogproxy`` offers a dual function, very handy during a FogBugz
migration, for example from an hosted solution to the On Demand version.

the ``fogproxy proxy`` command offers a ``scoutSubmit`` compatible API,
and saves all the submitted reports in a queue.

After the migration is completed, and later on, one can run
``fogproxy upload`` to forward the queued reports to the new server.

Added bonus, the proxy supports scouts attachments.


