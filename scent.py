import os
from sniffer.api import *
import nose

@file_validator
def py_files(filename):
      return filename.endswith('.py') or filename.endswith('.yaml') or filename.endswith('.rst')

@runnable
def execute_nose(*args):
    return nose.run(argv=list(args))

@runnable
def execute_sphinx(*args):
    return 0 == os.system('cd docs ; make')
