"""Database definitions."""

import logging
import time
import sqlalchemy as sa

logger = logging.getLogger('db')


def get_table(engine, keys, types):
    """Get, create, or alter a database table."""
    metadata = sa.MetaData(engine)
    columns = []
    for i, key in enumerate(keys):
        datatype = types[i]
        if datatype == 'int':
            ctype = sa.Integer
        elif datatype == 'double':
            ctype = sa.Float
        elif datatype == 'bool':
            ctype = sa.Boolean
        else:
            print("Unknown datatype:", datatype, "using String...")
            ctype = sa.String
        columns.append(sa.Column(key.replace('.', '_').lower(), ctype))
    if not engine.has_table('data'):
        table = sa.Table(
            'data', metadata,
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('timestamp', sa.DateTime),  # human-readable timestamp
            sa.Column('unix_timestamp', sa.Float),  # seconds since the epoch
            *columns)
    else:
        table = sa.Table('data', metadata, autoload=True)
        names = [name.lower() for name in table.columns.keys()]
        for i, col in enumerate(columns):
            if col.key.lower() not in names:
                with engine.connect() as conn:
                    conn.execute(sa.text(
                        "ALTER TABLE data ADD COLUMN {:s} {:s}".format(
                            col.key, str(col.type)))),

    metadata.create_all()
    return table


def create_sql_table(uri, keys, dtypes):
    """Create a remote SQL table (preferably Postgres)."""
    engine = sa.create_engine(uri)
    table = get_table(engine, keys, dtypes)
    return engine, table


def get_data_between(engine, start, stop):
    """Return data between the timestamps ``start`` and ``stop``."""
    logger.debug(str(start) + ', ' + str(stop))
    assert stop >= start
    stmt = "SELECT * FROM data WHERE unix_timestamp BETWEEN {start:f} AND {stop:f}".format(
        start=start, stop=stop)
    with engine.connect() as conn:
        result = conn.execute(sa.text(stmt))
        data = result.fetchall()
        columns = result.keys()

    output = {}
    for i, col in enumerate(columns):
        if col == 'id':
            continue
        output[col] = [x[i] for x in data]
    return output


def get_data_since(engine, timestamp):
    """Return the data since the given timestamp.

    Note that this does *not* take into account timezones
    anywhere. That would probably be a good thing to fix.

    """
    output = get_data_between(engine, timestamp, time.time())
    return output


def insert_row(engine, table, data):
    """Insert a new row into the table."""
    with engine.connect() as conn:
        conn.execute(table.insert().values(**data))
