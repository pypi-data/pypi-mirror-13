HitchPostgres
=============

HitchPostgres is a plugin for the Hitch test framework that lets you run and
interact with Postgres in an isolated way as part of a test.

Before starting the service, it runs the initdb command to create all required
data files for a postgresql database in the .hitch directory. This means that
whatever you do, you will not interfere with the system postgres files. The
system postgres does not even have to be running.

After starting the service, it creates any users and databases specified that
may be required for your app to start.

During the test it provides convenience functions psql, pg_dump and pg_restore
so that you can interact with the database using IPython or in your test.

Use
===

See: https://hitchtest.readthedocs.org/en/latest/api/postgres.html


Features
========

* Creates data files from scratch using initdb in the .hitch directory. Complete isolation of data from system postgres.
* Starts up on a separate thread in parallel with other services when running with HitchServe_, so that your integration tests run faster.
* Run the server on whatever port you like.
* Version set explicitly to prevent "works on my machine" screw ups caused by running different versions of Postgres.


.. _HitchServe: https://github.com/hitchtest/hitchserve
.. _DjangoRemindMe: https://github.com/hitchtest/django-remindme
