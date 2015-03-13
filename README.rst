==========
rowstextio
==========

One of the fastest ways to load data into a `PostgreSQL <http://www.postgresql.org/>`_ table is to use the `COPY <http://www.postgresql.org/docs/9.4/static/sql-copy.html>`_ SQL command that copies data from a file or from a stream directly into the table. This command is often used when loading large amounts of data from a foreign source into the database.

Sometimes you might also want to move data from a third party database into a PostgreSQL database. One way to do it could be to export the data into the appropriate format (usually CSV) and the use the COPY command to load the file into the table. Although this gets the job done, it's cumbersome and inflexible, specially if the query that generates the data requires special parameters. This is the problem this package tries to solve.

RowsTextIO is a read-only unicode character and line based interface to stream I/O from the result of a database query. This stream can be given as a parameter to the `psycopg <http://initd.org/psycopg/>`_'s cursor `copy_from <http://initd.org/psycopg/docs/cursor.html#cursor.copy_from>`_ method to load the data into the target table.

I've only tried this with PostgreSQL, but it should work with other database engines that support loading data from a stream.

Requirements
============

The only requirement for this package is `unicodecsv <https://github.com/jdunck/python-unicodecsv>`_, but in can be easily modified to work with Python's standard `csv <https://docs.python.org/2/library/csv.html>`_ module (In particular using the UnicodeWriter presented in the `examples <https://docs.python.org/2/library/csv.html#examples>`_ section).

Example
=======

The following session shows the typical use case for the package.

::

    >>>> import psycopg2
    >>>> import mysql.connector
    >>>> source_connection = mysql.connector.connect(**settings.XAPOUSERS_CONNECTION_SETTINGS)
    >>>> target_connection = psycopg2.connect(**settings.WAREHOUSE_CONNECTION_SETTINGS)
    >>>> from rowstextio import RowsTextIO
    >>>> source_cursor = source_connection.cursor()
    >>>> target_cursor = target_connection.cursor()
    >>>> f = RowsTextIO(source_cursor, 'SELECT * FROM source_table WHERE id <> %(id)s', {'id': 42})
    >>>> target_cursor.copy_expert('COPY target_table FROM STDIN CSV', f)
    >>>> target_cursor.close()
    >>>> source_cursor.close()

Assuming that the target table schema is compatible with the rows resulting from the query, the data should be loaded by now.