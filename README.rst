Phone Reporting System
======================

This is an experimental project that I'm working on, that replicates a real world scenario. 

I've created a database that I've populated with random call statistics. The application is going to going to provide authenticated users, with a reporting interface to this data.


**************
Phone Database
**************
First to create the database for the test phone data:

.. code-block:: sql

  psql
  CREATE USER [username] WITH PASSWORD '[password]';
  CREATE DATABASE [dbname] WITH OWNER [username];
  ALTER USER [username] WITH SUPERUSER;

I've then created a few SQL commands in the `create-commands.sql`_. file to create the simple schema which need to be executed.

The database can then be populated by running the python_db.py script.


************
Django Database
************
For the Django database, create as standard:

.. code-block:: sql

  psql
  CREATE USER [username] WITH PASSWORD '[password]';
  CREATE DATABASE [dbname] WITH OWNER [username];
  ALTER USER [username] WITH SUPERUSER;


******
NOTES
******
A few general notes for now, regarding the calls in the database:

.. code-block:: sql

  ch_internal_external = 0   /* internal */ 
  ch_internal_external = 1   /* external */ 

  ch_direction = 0    /* inbound */ 
  ch_direction = 1    /* outbound */ 



.. _create-commands.sql: configuration/db/create-commands.sql
