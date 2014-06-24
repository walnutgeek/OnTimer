'''
Created on Jun 23, 2014

@author: sergeyk
'''
import subprocess

def parseCmdLine(input):
    acc = ''
    delim = None
    for x in input:
        if delim:
            if x == delim:
                delim = None
                yield acc
                acc = ''
            else:
                acc += x
        else:
            if "'" == x :
                delim = "'"
            elif '"' == x :
                delim = '"'
            elif ' ' == x :
                if acc:
                    yield acc
                    acc = ''
            else:
                acc += x
    
    if acc:
        yield acc

class Runner:
    def __init__(self,node):
        pass
        
        
class ProcessRunner(Runner):
    def __init__(self,node):
      self.cmd = node('cmd').split()
    
    def run(self,):
        subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)