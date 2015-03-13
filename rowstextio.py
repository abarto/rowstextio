from __future__ import absolute_import, unicode_literals

import unicodecsv

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from io import TextIOBase, BytesIO


class RowsTextIO(TextIOBase):
    """
    A read-only unicode character and line based interface to stream I/O from the result of a
    database query.
    """
    def __init__(self, cursor, query, parameters=None, rows_per_fetch=500):
        self._cursor = cursor
        self._query = query
        self._parameters = parameters
        self._rows_per_fetch = rows_per_fetch

        self._buffer = BytesIO()
        self._rows = None

        self._cursor.execute(self._query, parameters)

    def readable(self):
        return True

    def _fetch_rows(self):
        self._rows = self._cursor.fetchmany(self._rows_per_fetch)

    def _write_rows_onto_buffer(self):
        self._buffer.close()
        self._buffer = BytesIO()

        writer = unicodecsv.writer(self._buffer, encoding='utf-8', errors='ignore')
        writer.writerows(self._rows)

        self._buffer.seek(0L)

    def read(self, n=None):
        read_buffer = StringIO()

        if n is not None:
            # Read a fixed amount of bytes

            left_to_read = n
            while left_to_read > 0:
                # Keep reading from the buffer

                read_from_buffer = self._buffer.read(left_to_read)

                if len(read_from_buffer) > 0:
                    read_buffer.write(unicode(read_from_buffer))
                elif len(read_from_buffer) < left_to_read:
                    # We read less than the remaining bytes. Fetch more rows.

                    self._fetch_rows()
                    self._write_rows_onto_buffer()

                    if len(self._buffer.getvalue()) == 0L:
                        # There are no more rows, break the loop
                        break

                left_to_read -= len(read_from_buffer)
        else:
            # Read all the rows

            while True:
                read_from_buffer = self._buffer.read()

                if len(read_from_buffer) > 0:
                    read_buffer.write(read_from_buffer)
                else:
                    # We emptied the buffer. Fetch more rows.

                    self._fetch_rows()
                    self._write_rows_onto_buffer()

                    if len(self._buffer.getvalue()) == 0L:
                        # There are no more rows, break the loop
                        break

        read_result = read_buffer.getvalue()
        read_buffer.close()

        return read_result