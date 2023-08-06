#!/usr/bin/env python3

"""
    pyprocessor: Preprocessor program
    Copyright (C) 2015  Alfredo Mungo <alfredo.mungo@openmailbox.org>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import os.path
import argparse
import io

__version__ = '2.0.0'

DEFAULT_CODE_BEGIN, DEFAULT_CODE_END = '<%', '%>'
DEFAULT_VAR_BEGIN, DEFAULT_VAR_END = '@@', '@@'

def _decode_vars(defs):
  """
    Converts an iterable of strings in the form 'name=value' into a dictionary object and returns it.
  """
  res = dict()
  
  for d in defs:
    name, value = d.split('=', 1)
    res[name] = value

  return res

def process_str(data, svars = dict(), code_boundaries = (DEFAULT_CODE_BEGIN, DEFAULT_CODE_END), var_boundaries = (DEFAULT_VAR_BEGIN, DEFAULT_VAR_END)):
  """
    Substitutes code regions of `data` delimited by code_begin and code_end with their output, then substitutes
    variable regions delimited by var_begin and var_end with variables defined on the command line and/or defined
    or processed by code regions.

    ARGUMENTS:
      data: The data to process as a string
      
      For other arguments see process_str().

    Example:
      A code region <% print('hello', end='') %> will be substituted with 'hello' (without quotes).

      A variable region @@TODAY@@ will be substituted with 'monday' (without quotes) if the command line argument
      `-D TODAY=monday` is supplied.
  """

  # Ignore empty variable and space variables, they could lead to substitution errors
  for k in tuple(svars.keys()):
    if k.strip(' ') == '':
      del svars[k]

  code_begin, code_end = code_boundaries
  var_begin, var_end = var_boundaries
  old_stdout = sys.stdout
  idx = data.find(code_begin)

  while idx >= 0:
    idx_end = data.find(code_end, idx) + len(code_end)
    sys.stdout = io.StringIO()

    if idx_end < 0:
      sys.exit('ERROR: Unterminated code block')

    full_code = data[idx:idx_end]
    code = full_code[len(code_begin):-len(code_end)].strip()

    exec(compile(code, '<string>', 'exec'), None, svars)
    
    data = data[:idx] + sys.stdout.getvalue() + data[idx_end:]

    idx = data.find(code_begin, idx + len(sys.stdout.getvalue()))
    sys.stdout.close()

  sys.stdout = old_stdout

  for name in svars:
    data = data.replace(var_begin + name + var_end, str(svars[name]))

  return data

def process_file(in_path, out_path, overwrite = False, svars = dict(), code_boundaries = (DEFAULT_CODE_BEGIN, DEFAULT_CODE_END), var_boundaries = (DEFAULT_VAR_BEGIN, DEFAULT_VAR_END)):
  """
    Processes a single file.

    ARGUMENTS:
      in_path: Path to input file
      out_path: Path to output file
      overwrite: True if existing output file should be overwritten
      svars: A dictionary of variables to substitute during data processing
      code_boundaries: A tuple of two elements representing the code region delimiters
      var_boundaries: A tuple of two elements representing the variable delimiters
  """
  if os.path.exists(out_path) and not overwrite:
    sys.exit('ERROR: Output file exists and --force flag not used.')

  # Read template
  if in_path != '-':
    with open(in_path, 'r') as in_file:
      data = in_file.read()
  else:
    data = sys.stdin.read()

  # Preprocess data
  data = process_str(data, svars, code_boundaries, var_boundaries)

  # Save result
  if out_path != '-':
    with open(out_path, 'w') as out_file:
      out_file.write(data)
  else:
    print(data, end='')

def _parse_arguments(args):
  parser = argparse.ArgumentParser(
    prog='pyprocessor',
    description='Python 3 preprocessor program',
    add_help=True,
    allow_abbrev=False
  )

  parser.add_argument('--input', '-i', action='store', help='The input file.', default='-')
  parser.add_argument('--output', '-o', action='store', help='The output file.', default='-')
  parser.add_argument('--define', '-D', action='append', help='Define a variable in the form NAME=VALUE. Can be used multiple times.')
  parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing files.')
  parser.add_argument('--code-boundaries', '-cb', action='store', help='Set the code boundary symbols.', nargs=2, default=(DEFAULT_CODE_BEGIN, DEFAULT_CODE_END))
  parser.add_argument('--var-boundaries', '-vb', action='store', help='Set the variable boundary symbols.', nargs=2, default=(DEFAULT_VAR_BEGIN, DEFAULT_VAR_END))

  return parser.parse_args(args)
  
def main(args):
  # Parse input
  ns = _parse_arguments(args)

  # Validate input

  # Setup environment
  svars = _decode_vars(ns.define) if ns.define is not None else dict()

  # Do work on file
  process_file(ns.input, ns.output, ns.force, svars, tuple(ns.code_boundaries), tuple(ns.var_boundaries))

if __name__ == '__main__':
  main(sys.argv[1:])
