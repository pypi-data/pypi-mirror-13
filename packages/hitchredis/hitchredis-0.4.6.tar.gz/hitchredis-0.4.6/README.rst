HitchRedis
==========

HitchRedis is a plugin for the Hitch testing framework that lets you run and
interact with Redis during your integration tests.


Use
===

See: https://hitchtest.readthedocs.org/en/latest/api/redis.html


Features
========

* Starts up on a separate thread in parallel with other services when running with HitchServe_, so that your integration tests run faster.
* Contains subcommand to interact with the CLI.
* Run the server on whichever port you like.
* Version must be set explicitly to prevent "works on my machine" screw ups caused by different versions of Redis being installed.


.. _HitchServe: https://github.com/hitchtest/hitchserve
.. _DjangoRemindMe: https://github.com/hitchtest/django-remindme
