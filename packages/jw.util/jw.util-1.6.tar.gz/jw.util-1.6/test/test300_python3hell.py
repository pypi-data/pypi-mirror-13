"""
Tests for python3hell module

Only meaningfull with tox
"""
from __future__ import unicode_literals
import sys
from jw.util.python3hell import Bytes2Str, SetDefaultEncoding
from nose.tools import eq_

def test10_Bytes2Str():
    eq_(Bytes2Str(b'x'), 'x')

def test20_SetDefaultEncoding():
    SetDefaultEncoding('utf-8')
    eq_(sys.getdefaultencoding(), 'utf-8')
