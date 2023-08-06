# -*- coding: utf-8 -*-

import os
from code import interact
from datetime import datetime

import tablib
import psycopg2
from docopt import docopt
from psycopg2.extras import register_hstore, NamedTupleCursor
from psycopg2.extensions import cursor as _cursor


DATABASE_URL = os.environ.get('DATABASE_URL')

PG_INTERNAL_TABLES_QUERY = "SELECT * FROM pg_catalog.pg_tables"
PG_TABLES_QUERY = """
    SELECT
        *
    FROM
        pg_catalog.pg_tables
    WHERE
        schemaname != 'pg_catalog' AND
        schemaname != 'information_schema'
"""


class RecordsCursor(NamedTupleCursor):
    """An enhanced cursor that generates Records."""
    try:
        from collections import namedtuple
    except ImportError as _exc:
        def _make_nt(self):
            raise self._exc
    else:
        def _make_nt(self, namedtuple=namedtuple):
            RecordBase = namedtuple("Record", [d[0] for d in self.description or ()])

            # Extend the RecordsBase namedtuple, for enhanced API functionality.
            class Record(RecordBase):
                __slots__ = ()
                def keys(self):
                    return self._fields

                def __getitem__(self, key):
                    if isinstance(key, int):
                        return super(RecordBase, self).__getitem__(key)

                    if key in self.keys():
                        return getattr(self, key)

                    raise KeyError("Record contains no '{}' field.".format(key))

                @property
                def dataset(self):
                    """A Tablib Dataset containing the row."""
                    data = tablib.Dataset()
                    data.headers = self._fields

                    row = _reduce_datetimes(self)
                    data.append(row)

                    return data

                def export(self, format, **kwargs):
                    """Exports the row to the given format."""
                    return self.dataset.export(format, **kwargs)

                def get(self, key, default=None):
                    try:
                        return self[key]
                    except KeyError:
                        return default

            return Record


class ResultSet(object):
    """A set of results from a query."""
    def __init__(self, rows):
        self._rows = rows
        self._all_rows = []
        self.pending = True

    def __repr__(self):
        r = '<ResultSet size={} pending={}>'.format(len(self), self.pending)
        return r

    def __iter__(self):
        """Iterate over all rows, consuming the underlying generator
        only when necessary."""
        i = 0
        while True:
            # Other code may have iterated between yields,
            # so always check the cache.
            if i < len(self):
                yield self[i]
            else:
                # Throws StopIteration when done.
                yield next(self)
            i += 1


    def next(self):
        return self.__next__()

    def __next__(self):
        try:
            nextrow = next(self._rows)
            self._all_rows.append(nextrow)
            return nextrow
        except StopIteration:
            self.pending = False
            raise StopIteration('ResultSet contains no more rows.')

    def __getitem__(self, key):
        is_int = isinstance(key, int)

        # Convert ResultSet[1] into slice.
        if is_int:
            key = slice(key, key + 1)

        while len(self) < key.stop or key.stop is None:
            try:
                next(self)
            except StopIteration:
                break

        rows = self._all_rows[key]
        if is_int:
            return rows[0]
        else:
            return ResultSet(iter(rows))

    def __len__(self):
        return len(self._all_rows)

    def export(self, format, **kwargs):
        """Export the ResultSet to a given format (courtesy of Tablib)."""
        return self.dataset.export(format, **kwargs)

    @property
    def dataset(self):
        """A Tablib Dataset representation of the ResultSet."""
        # Create a new Tablib Dataset.
        data = tablib.Dataset()

        # Set the column names as headers on Tablib Dataset.
        first = self[0]

        data.headers = first._fields
        for row in self.all():
            row = _reduce_datetimes(row)
            data.append(row)

        return data


    def all(self):
        """Returns a list of all rows for the ResultSet. If they haven't
        been fetched yet, consume the iterator and cache the results."""

        # By calling list it calls the __iter__ method
        return list(self)

class Database(object):
    """A Database connection."""

    def __init__(self, db_url=None):
        # If no db_url was provided, fallback to $DATABASE_URL.
        self.db_url = db_url or DATABASE_URL

        if not self.db_url:
            raise ValueError('You must provide a db_url.')

        # Connect to the database.
        self.db = psycopg2.connect(self.db_url, cursor_factory=RecordsCursor)

        # Enable hstore if it's available.
        self._enable_hstore()
        self.open = True

    def close(self):
        """Closes the connection to the Database."""
        self.db.close()
        self.open = False

    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.close()

    def __repr__(self):
        return '<Database open={}>'.format(self.open)

    def _enable_hstore(self):
        """Enables HSTORE support, if available."""
        try:
            register_hstore(self.db)
        except psycopg2.ProgrammingError:
            pass

    def get_table_names(self, internal=False):
        """Returns a list of table names for the connected database."""

        # Support listing internal table names as well.
        query = PG_INTERNAL_TABLES_QUERY if internal else PG_TABLES_QUERY

        # Return a list of tablenames.
        return [r['tablename'] for r in self.query(query)]

    def query(self, query, params=None, fetchall=False):
        """Executes the given SQL query against the Database. Parameters
        can, optionally, be provided. Returns a ResultSet, which can be
        iterated over to get result rows as dictionaries.
        """

        # Execute the given query.
        c = self.db.cursor()
        c.execute(query, params)

        # Row-by-row result generator.
        row_gen = (r for r in c)

        # Convert psycopg2 results to ResultSet.
        results = ResultSet(row_gen)

        # Fetch all results if desired.
        if fetchall:
            results.all()

        return results

    def query_file(self, path, params=None, fetchall=False):
        """Like Database.query, but takes a filename to load a query from."""

        # If path doesn't exists
        if not os.path.exists(path):
            raise FileNotFoundError

        # If it's a directory
        if os.path.isdir(path):
            raise IsADirectoryError

        # Read the given .sql file into memory.
        with open(path) as f:
            query = f.read()

        # Defer processing to self.query method.
        return self.query(query=query, params=params, fetchall=fetchall)

def _reduce_datetimes(row):
    """Receives a row, converts datetimes to strings."""
    for i in range(len(row)):
        if hasattr(row[i], 'isoformat'):
            row = row._replace(**{row._fields[0]: row[i].isoformat()})
    return row


def cli():
    cli_docs ="""Records: SQL for Humans™
A Kenneth Reitz project.

Usage:
  records <query> <format> [-i] [--params <params>...] [--url=<url>]
  records (-h | --help)

Options:
  -h --help         Show this screen.
  --url=<url>       The database URL to use. Defaults to $DATABASE_URL.
  --params          Prameterized query. Subsequent arguments are treated as
                    parameters to the query.
  -i --interactive  An interactive interpreter.

Supported Formats:
   csv, tsv, json, yaml, html, xls, xlsx, dbf, latex, ods

   Note: xls, xlsx, dbf, and ods formats are binary, and should only be
         used with redirected output e.g. '$ records sql xls > sql.xls'.

Notes:
  - While you may specify a Postgres connection string with --url, records
    will automatically default to the value of $DATABASE_URL, if available.
  - Query is intended to be the path of a SQL file, however a query string
    can be provided instead. Use this feature discernfully; it's dangerous.
  - Records is intended for report-style exports of database queries, and
    has not yet been optimized for extremely large data dumps.
  - Interactive mode is experimental and may be removed at any time.
    Feedback, as always, is much appreciated!  --me@kennethreitz.org

Cake:
   ✨ 🍰 ✨
    """
    supported_formats = 'csv tsv json yaml html xls xlsx dbf latex ods'.split()

    # Parse the command-line arguments.
    arguments = docopt(cli_docs)
    # print arguments
    # exit()

    # Cleanup docopt parsing errors.
    if arguments['--params'] and arguments['<format>'] not in supported_formats:
        arguments['<params>'].insert(0, arguments['<format>'])
        arguments['<format>'] = None

    # Create the Database.
    db = Database(arguments['--url'])

    query = arguments['<query>']
    params = arguments['<params>']

    # Execute the query, if it is a found file.
    if os.path.isfile(query):
        rows = db.query_file(query, params)

    # Execute the query, if it appears to be a query string.
    elif len(query.split()) > 2:
        rows = db.query(query, params)

    # Otherwise, say the file wasn't found.
    else:
        print('The given query could not be found.')
        exit(66)

    # Interactive mode.
    if arguments['--interactive']:
        interactive_env = {'db': db, 'rows': rows}
        interact(interactive_env, local=interactive_env)
        exit()

    # Print results in desired format.
    if arguments['<format>']:
        print(rows.export(arguments['<format>']))
    else:
        print(rows.dataset)

# Run the CLI when executed directly.
if __name__ == '__main__':
    cli()




