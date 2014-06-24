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
    def __init__(self,node,event):
        self.cmd = parseCmdLine( node['cmd'].format( *event.vars ) )
    
    def run(self,ioloop):
        subprocess.Popen(self.cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)