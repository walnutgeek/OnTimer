import os
import shutil
import unittest
import time
import datetime


from nose.tools import eq_, with_setup
from .. import dpt


#to test if sniffer is not hanging uncomment next line & save
#raise Exception()


def test_Node():
    s31 = dpt.PathElem("s31")
    eq_(s31.s, 's')
    eq_(s31.n, 31)
    another_s31 = dpt.PathElem("s",31)
    eq_(s31, another_s31)
    
def test_Path():
    s31 = dpt.Path("s31")
    eq_(s31.elems[0].s, 's')
    eq_(s31.elems[0].n, 31)
    another_s31 = dpt.Path("s31")
    eq_(s31, another_s31)
    path = dpt.Path("z31g15")
    eq_(path.elems[0].s, 'z')
    eq_(path.elems[0].n, 31)
    eq_(path.elems[1].s, 'g')
    eq_(path.elems[1].n, 15)
    path = dpt.Path("l18r3")
    eq_(path.elems[0].s, 'l')
    eq_(path.elems[0].n, 18)
    eq_(path.elems[1].s, 'r')
    eq_(path.elems[1].n, 3)

    path = dpt.Path("e3")
    eq_(path.elems[0].s, 'z')
    eq_(path.elems[0].n, 31)
    eq_(path.elems[1].s, 'e')
    eq_(path.elems[1].n, 3)

    path = dpt.Path("")
    eq_(path.elems[0].s, 'z')
    eq_(path.elems[0].n, 31)
    
    try:
        path = dpt.Path("r3")
        eq_(True,False)
    except ValueError:
        pass
    try:
        path = dpt.Path("e17E3")
        eq_(True,False)
    except ValueError:
        pass
    try:
        path = dpt.Path("q3")
        eq_(True,False)
    except ValueError:
        pass


