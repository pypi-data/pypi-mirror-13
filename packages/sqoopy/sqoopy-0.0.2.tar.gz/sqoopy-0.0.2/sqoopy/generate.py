# -*- coding: utf-8 -*-

import dataset 


class Db(object):
  """
  A simple representation of a database connection.
  """
  def __init__(self, conn):
    if conn.startswith('jdbc:'):
      self.conn = dataset.connect(conn.replace('jdbc:', ''))
    else:
      try:
        self.conn = dataset.connect(conn)
      except Exception as e:
        raise ValueError, \
          'Could not connect to {} because {}'.format(conn, e.message)

    # cache list of tables.
    self._tables = self.conn.tables

  @property
  def tables(self):
    """
    Programmatically determine a DB's list of tables.
    """
    return self._tables


class Sqoop(object):
  """
  Generate a sqoop import command for a table.
  """
  def __init__(self, conn, table, target_dir, sqoop_opts=[]):
    self.cmd = "sqoop import --connect={} --table={} --target-dir={} {}"\
      .format(conn, table, target_dir, " ".join(sqoop_opts)).strip()

def generate(opts, sqoop_opts):
  """
  Generate a list of sqoop commands given command-line options.
  """
  # connect to database.
  db = Db(opts.connect)

  # determine / validate list of tables and generate target-dir
  tables = []

  # custom list
  if len(opts.tables):
    for t in opts.tables:
      if t not in db.tables:
          raise ValueError, \
            'Table {} does not exist'.format(t)
      td = opts.target_dir.format(table=t)
      if not td.endswith('/'):
        td += '/'
      tables.append((t, td))
  
  # all tables.
  else:
    for t in db.tables:
      td = opts.target_dir.format(table=t)
      if not td.endswith('/'):
        td += '/'
      tables.append((t, td))

  # Generate all commands
  return [Sqoop(opts.connect, t[0], t[1], sqoop_opts).cmd for t in tables]