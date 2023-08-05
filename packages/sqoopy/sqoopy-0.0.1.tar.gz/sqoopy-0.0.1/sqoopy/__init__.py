# -*- coding: utf-8 -*-
'''
Usage: sqoopy [--connect=connect] [--target-dir=target_dir] [--tables=tables] **sqoop-options

sqoopy: Generate sqoop custom import statements

Arguments:
  connect    The database url to connect to.'
  target_dir The directory to send output to. If sending to s3, use '{table}' to insert the table name into the directory.
  tables    (Optional) comma-separated list of tables that need to be inspected. If not supplied, all tables will be imported.
  **sqoop-options Passthrough sqoop options to each command.
'''

import argparse

from .generate import generate

def run():
  """
  Given a jdbc connection string and and an optional list of tables, 
  construct a series of sqoop import commands and print them to the console.
  """
  
  # argument parsing

  def table_list(value):
    return [str(v).strip() for v in value.split(',') if v.strip()]

  parser = argparse.ArgumentParser('sqoopy', description='Python CLI to generate custom sqoop import statements.')
  parser.add_argument('-c', '--connect', type=str, help='A jdbc connection string.')
  parser.add_argument('-d', '--target-dir', type=str, 
    help='The directory to send output to. If sending to s3, use "{table}" to insert the table name into the directory. EG: s3://my-bucket/{table}/')
  parser.add_argument('-t', '--tables', type=table_list, 
      help='(Optional) comma-separated list of tables that need to be inspected. If not supplied, all tables will be imported.',
      default='')

  # allow for arbitrary passthrough args.
  opts, sqoop_opts = parser.parse_known_args()
  print("\n".join(generate(opts, sqoop_opts)))
