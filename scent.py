from sniffer.api import *

@file_validator
def py_files(filename):
      return filename.endswith('.py') or filename.endswith('.yaml')
