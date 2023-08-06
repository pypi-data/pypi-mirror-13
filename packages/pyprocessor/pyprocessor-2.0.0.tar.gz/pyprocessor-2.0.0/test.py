#!/usr/bin/env python3

import pyprocessor
import unittest
import tempfile
import os

class PreprocessorTestCase(unittest.TestCase):
  def test_preprocess_string(self):
    input1 = 'This is a @@TEST@@ <% print("string", end="") %>' # TEST = 'short test'
    output1 = 'This is a short test string'

    input2 = 'This is a $$TEST$$ <$ TEST="long test" $>.'
    output2_vars = 'This is a foo test <$ TEST="long test" $>.' # TEST = 'foo test'
    output2_code = 'This is a $$TEST$$ .'
    output2 = 'This is a long test .'

    # Default
    self.assertEqual(pyprocessor.process_str(input1, svars=dict(TEST='short test')), output1)
    self.assertEqual(pyprocessor.process_str(input2), input2)

    # Variable boundaries changed
    self.assertEqual(pyprocessor.process_str(input2, var_boundaries=('$$', '$$'), svars=dict(TEST='foo test')), output2_vars)

    # Code boundaries changed
    self.assertEqual(pyprocessor.process_str(input2, code_boundaries=('<$', '$>')), output2_code)

    # Variable and code boundaries changed
    self.assertEqual(pyprocessor.process_str(input2, code_boundaries=('<$', '$>'), var_boundaries=('$$', '$$')), output2)

  def test_process_file(self):
    in_file = tempfile.NamedTemporaryFile(mode='w', encoding="utf-8", delete=False)
    out_file = tempfile.NamedTemporaryFile(mode='w', encoding="utf-8", delete=False)
    out_file.close()

    data_in = '''<html>
  <head>
    <title>@@TITLE@@</title>
  </head>
  <body>
    <% print('2*2 is {}'.format(2*2)) %>
  </body>
</html>'''

    result = pyprocessor.process_str(data_in, svars=dict(TITLE='Test file')) # Safe to use process_str here, because it is tested in its own test function
    in_file.write(data_in)
    in_file.close()

    pyprocessor.process_file(in_file.name, out_file.name, overwrite=True, svars=dict(TITLE='Test file'))

    with open(out_file.name, 'r') as f:
      output = f.read()

    os.unlink(in_file.name)
    os.unlink(out_file.name)

    self.assertEqual(output, result)

  def test_substitution(self):
    input = '<% print("a", end="")%><% print("b", end="") %>'
    output = 'ab'

    self.assertEqual(pyprocessor.process_str(input), output)

    input = '@@first@@@@second@@ @@third@@'
    output = 'ab g'
    svars = { 'first': 'a', 'second': 'b', '': 'c' , ' ': 'd', '     ': 'e', 'third': 'g'}

    self.assertEqual(pyprocessor.process_str(input, svars=svars), output)

if __name__ == '__main__':
  unittest.main()
