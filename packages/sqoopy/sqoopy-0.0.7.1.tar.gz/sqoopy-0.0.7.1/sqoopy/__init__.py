# -*- coding: utf-8 -*-
import re 
import copy
import math
import argparse
from argparse import Namespace

import dataset 


class Db(object):
  """
  A database connection and information on it's tables.
  """
  
  re_uri = re.compile(r"^(?P<driver>[^:]+)://(?P<username>[^:]+):(?P<password>[^@]*)@(?P<host>[^/]+)/(?P<database>[A-Za-z_]+)$")

  def __init__(self, conn_str, **kw):
    
    # ignore jdbc for now.
    if conn_str.startswith('jdbc:'):
      conn_str = conn.replace('jdbc:', '')
    self.conn_str = conn_str
    self.conn = dataset.connect(self.conn_str)
    # cache list of table names.
    self.tablenames = kw.get('tables', self.conn.tables)

  @property
  def config(self):
    """
    database configurations parsed from a db uri
    """
    m = self.re_uri.search(self.conn_str)
    if not m:
      raise ValueError, 'Invalid database-uri: {}'.format(conn)
    return m.groupdict()

  @property
  def tables(self):
    """
    A lookup of a DB's tables and their sizes
    """
    tables = {}

    results = self.conn.query(\
      """SELECT 
          table_name as tablename,
          table_rows as rows,
          round(((data_length + index_length) / 1024 / 1024), 2) as mbs
         FROM information_schema.tables
         WHERE table_schema = "{}"
         ORDER BY tablename asc
      """.format(self.config['database']))

    for r in results:
      if r['tablename'] in self.tablenames:
        tables[r['tablename']] = dict(r.items())
    return tables


def generate(args=[], **opts):
  """
  Generate a list of sqoop commands given command-line/progrmttic options.

  """
  opts.setdefault('min_mbs', 10)
  opts.setdefault('max_mbs', 100)
  opts.setdefault('min_mappers', 1)
  opts.setdefault('max_mappers', 500)
  opts.setdefault('password', '')

  # connect to db + parse config string
  db = Db(opts['connect'], **opts)
  opts.update(db.config)

  # reformat connection string:
  opts['connect'] = "jdbc:{driver}://{host}/{database}".format(**opts)

  # command pattern
  cmd = """
  sqoop import \
    --connect={connect} \
    --username={username} \
    --password={password} \
    --table={tablename} \
    --target-dir={target_dir} \
    --num-mappers={num_mappers} \
    {args}
  """

  # for each table compute optimal number of mappers + format table name.
  for tn, info in db.tables.items():
    o = copy.copy(opts)
  
    # format target dir
    td = o['target_dir'].format(table=tn)
    if not td.endswith('/'):
      td += '/'
    o['target_dir'] = td

    # num_mappers
    min_chunks = int(math.floor(info['mbs'] / opts['min_mbs']))
    max_chunks = int(math.floor(info['mbs'] / opts['max_mbs']))

    # catch small tables
    if min_chunks < 1 or max_chunks < 1:
      o['num_mappers'] = 1
    else:
      o['num_mappers'] = max_chunks

    # limit mappers
    if o['num_mappers'] < o['min_mappers']:
      o['num_mappers'] = o['min_mappers']
    elif o['num_mappers'] > o['max_mappers']:
      o['num_mappers'] = ['max_mappers']

    # passthru args
    o['args'] = " ".join(args)
    o['tablename'] = tn

    # generate command
    yield cmd.format(**o).replace('  ', ' ').strip()


def cli():
  """
  Given a jdbc connection string and and an optional list of tables, 
  construct a series of sqoop import commands and print them to the console.
  """
  
  # argument parsing

  def _table_list(value):
    return [str(v).strip() for v in value.split(',') if v.strip()]

  parser = argparse.ArgumentParser('sqoopy', description='Python CLI to generate custom sqoop import statements.')
  parser.add_argument('-c', '--connect', type=str, help='A jdbc connection string.')
  parser.add_argument('-d', '--target-dir', type=str, 
    help='The directory to send output to. If sending to s3, use "{table}" to insert the table name into the directory. EG: s3://my-bucket/{table}/')
  parser.add_argument('-t', '--tables', type=_table_list, 
      help='(Optional) comma-separated list of tables that need to be inspected. If not supplied, all tables will be imported.',
      default='')

  # allow for arbitrary passthrough args.
  opts, args = parser.parse_known_args()
  for cmd in generate(args, **opts.__dict__):
    print cmd
