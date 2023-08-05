# -*- coding: utf-8 -*-
import re 
import copy
import math
import sys
import argparse
import subprocess
from multiprocessing import Pool
import shlex

import dataset 

GENERIC_ARGS = [
  '-conf', '-D', '-fs', '-jt', '-files', 
  '-libjars', '-archives'
]

class Db(object):
  """
  A database connection and information on it's tables.
  """
  
  re_uri = re.compile(r"^(?P<driver>[^:]+)://(?P<user>[^:]+):(?P<password>[^@]*)@(?P<host>[^:]+):(?P<port>[0-9]+)/(?P<database>[A-Za-z_]+)$")

  def __init__(self, conn_str, **opts):
    
    # ignore jdbc for now.
    if conn_str.startswith('jdbc:'):
      conn_str = conn.replace('jdbc:', '')
    self.conn_str = conn_str
    self.conn = dataset.connect(self.conn_str)
    # cache list of table names.
    self.tablenames = opts.get('tables', self.conn.tables)
    self.excl_tablenames = opts.get('excl_tables', [])

  @property
  def config(self):
    """
    database configurations parsed from a db uri
    """
    m = self.re_uri.search(self.conn_str)
    if not m:
      raise ValueError, 'Invalid database-uri: {}'.format(self.conn_str)
    return m.groupdict()

  @property
  def tables(self):
    """
    A lookup of a DB's tables and their sizes
    """
    # query information schema for table sizes
    results = self.conn.query(\
      """SELECT 
          table_name as tablename,
          table_rows as rows,
          round(((data_length + index_length) / 1024 / 1024), 2) as mbs
         FROM information_schema.tables
         WHERE table_schema = "{}"
         ORDER BY tablename asc
      """.format(self.config['database']))

    # include / exclude tables
    tables = {}
    for r in results:
      if r['tablename'] in self.tablenames:
        tables[r['tablename']] = dict(r.items())
    for k in self.excl_tablenames
      tables.pop(k, None)

    return tables


def gen(**opts):
  """
  Generate a list of sqoop commands given command-line/progrmttic options.

  """
  # control chunk size
  opts.setdefault('min_mbs', 1)
  opts.setdefault('max_mbs', 20)

  # usually no password
  opts.setdefault('password', '')
  opts.setdefault('sqoop_args', ['--hive-drop-import-delims'])

  # connect to db + parse config string
  db = Db(opts['connect'], **opts)
  opts.update(db.config)

  # reformat connection string:
  opts['connect'] = "jdbc:{driver}://{host}:{port}/{database}".format(**opts)

  # command pattern
  cmd = """
  sqoop import \
    {generic_args} \
    --connect={connect} \
    --username={user} \
    --password={password} \
    --table={tablename} \
    --target-dir={target_dir} \
    --num-mappers={num_mappers} \
    {import_args}
  """
  # for each table compute optimal number of mappers + format table name.
  for tn, info in db.tables.items():
    o = copy.copy(opts)
  
    # passthru tablename
    o['tablename'] = tn

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

    # generate command
    cmd = cmd.format(**o)
    o['cmd'] = re.sub('\s+', ' ', cmd).strip()
    yield o


def run(**opts):
  """
  Run commands in a pool, throttling based on size.
  """
  _p = Pool(opts['pool_size'])
  pooled = []
  serial = []
  for cmd in gen(**opts):
    if cmd['num_mappers'] > cmd['max_pool_maps'] or cmd['pool_size'] == 1:
      serial.append(cmd)
    else:
      pooled.append(cmd)

  try:
    if len(pooled):
      # pooled execution
      _p.map(_exec, pooled)

    if len(serial):
      # serial execution
      for cmd in serial:
        return _exec(cmd)

  except Exception as e:
    sys.stderr.write(e.message)
    sys.exit(1)

def cli():
  """
  Given a jdbc connection string and and an optional list of tables, 
  construct a series of sqoop import commands and print them to the console.
  """
  opts = _get_cli_opts()
  if opts['generate']:
    for cmd in gen(**opts):
      sys.stdout.write(cmd['cmd'] + "\n")
  else:
    for line in run(**opts).split("\n"):
      sys.stdout.write(line + "\n")
  sys.exit(0)


def _exec(opts):
  """
  Execute a command, handling erros and logging properly.
  """
  args = shlex.split(opts['cmd'])
  process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()
  exitcode = process.wait()
  if exitcode != 0:
    for line in stderr.split("\n"):
      sys.stdout.write(line + "\n")
    raise RuntimeError(stderr)
  return stdout

def _get_cli_opts():
  """
  Get options from command line arguments.
  """

  # argument parsing

  def _lst(value):
    return [str(v).strip() for v in value.split(',') if v.strip()]

  parser = argparse.ArgumentParser('sqoopy',
      description='Python CLI to generate custom sqoop import statements.')
  parser.add_argument('-c', '--connect', type=str, 
      help='A jdbc connection string.')
  parser.add_argument('-d', '--target-dir', type=str, 
      help='The directory to send output to. If sending to s3, use "{table}" to insert the table name into the directory. EG: s3://my-bucket/{table}/')
  parser.add_argument('-t', '--tables', type=_lst, 
      help='(Optional) comma-separated list of tables that need to be inspected. If not supplied, all tables will be imported.',
      default='')
  parser.add_argument('-x', '--excl-tables', type=_lst, 
      help='(Optional) comma-separated list of tables to exclude. If not supplied and --tables not specified, all tables will be imported.',
      default='')
  parser.add_argument('--generate', action="store_true", default=False,
      help='Just generate the sqoop commands and print them to the console.')
  parser.add_argument('--pool-size', type=int, default=1,
      help='The number of commands to execute concurrently')
  parser.add_argument('--max-pool-maps', type=int, default=15,
      help='The  number of mappers at which the import of a table will occur serially, after all other pooled imports are complete')
  parser.add_argument('--min-mbs', type=int, default=1,
      help='The minimim chunk size (in MBs). Used to determine the number of mappers needed for a given table')
  parser.add_argument('--max-mbs', type=int, default=20,
      help='The maximum chunk size (in MBs). Used to determine the number of mappers needed for a given table')


  # allow for arbitrary passthrough args.
  opts, args = parser.parse_known_args()
  opts = opts.__dict__
  opts['generic_args'] = ""
  opts['import_args'] = ""
  for arg in args:
    a =  " {}".format(arg)
    if any([arg.strip().startswith(g) for g in GENERIC_ARGS]):
      opts['generic_args'] += a
    else:
      opts['import_args'] += a

  return opts
