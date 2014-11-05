from __future__ import print_function

"""
run nosetests from module root
"""
from hashlib import sha224
import os
import time
import unittest
from pprint import pprint
import numpy as np

from numpy.testing import assert_array_equal, \
                          assert_array_almost_equal

from isnobal import IPW, packToHd5

class Test_readIPW(unittest.TestCase):
    
    def test_read(self):
        ipw = IPW('tests/testIPWs/in.0051', rescale=False)
        """
        with open('tests/validation/in.0051.validation.txt', 'wb') as f:
            for L in ipw.bands[0].data:
                f.write('\t'.join(map(str, L)))
                f.write('\r\n')
        """
        with open('tests/validation/in.0051.validation.txt') as f:
            for d, L in zip(ipw.bands[0].data, f.readlines()):
                x =  np.array(map(int, L.split('\t')))
                assert_array_equal(d, x)
                            
    def test_read_scale(self):
        ipw = IPW('tests/testIPWs/in.0051')
        """
        with open('tests/validation/in.0051.validation2.txt', 'wb') as f:
            for L in ipw.bands[0].data:
                f.write('\t'.join(map(str, L)))
                f.write('\r\n')
        """
        with open('tests/validation/in.0051.validation2.txt') as f:
            for d, L in zip(ipw.bands[0].data, f.readlines()):
                x = np.array(map(float, L.split('\t')))
                assert_array_almost_equal(d, x, 3)
                            
         
class Test_translate(unittest.TestCase):               
    def test_translate001(self):
        ipw = IPW('tests/testIPWs/in.0051', rescale=False)
        ipw.translate('tests/tmp/in.0051')

        fns = [ 'tests/tmp/in.0051.00.tif',
                'tests/tmp/in.0051.01.tif',
                'tests/tmp/in.0051.02.tif',
                'tests/tmp/in.0051.03.tif',
                'tests/tmp/in.0051.04.tif' ]

        """
        f = open('tests/hash.txt', 'wb')
        for fn in fns:
            f.write(sha224(open(fn).read()).hexdigest())
            f.write('\r\n')
        """
        digests = [ 'cec6ccac357a402e00327497dff972e36552fcf3d1e6c56fcc4b0f37',
                    '3c7a650afcec246e94e2e4af54d46ff3b539d8b52dca59b2bd0f28eb',
                    '695fa00321a22c079e42dd5d6a4d5f434673e2930b035f8c32ae8852',
                    '695fa00321a22c079e42dd5d6a4d5f434673e2930b035f8c32ae8852',
                    '3c7a650afcec246e94e2e4af54d46ff3b539d8b52dca59b2bd0f28eb' ]
        
        for fn in fns:
            assert os.path.exists( fn )

        for i, fn in enumerate(fns):
            hd = sha224(open(fn).read()).hexdigest()
            assert hd == digests[i]
            
        for fn in fns:
            os.remove( fn )
            
    def test_translate002(self):
        ipw = IPW('tests/testIPWs/in.0051')
        ipw.translate('tests/tmp/in.0051')

        fns = [ 'tests/tmp/in.0051.00.tif',
                'tests/tmp/in.0051.01.tif',
                'tests/tmp/in.0051.02.tif',
                'tests/tmp/in.0051.03.tif',
                'tests/tmp/in.0051.04.tif' ]
        """
        f = open('tests/hash.txt', 'wb')
        for fn in fns:
            f.write(sha224(open(fn).read()).hexdigest())
            f.write('\r\n')
        """ 
        digests = [ 'a3b7a3388b910ecfeda89ff7817d35693e0e59a69f01ea5c3c5d11ab',
                    '6d45a397133a5482eb13e8ca053cd9319e48e244844a1135410f64bf',
                    '65ab03d5100235deb0cc772236394d0f1d4002b9b8a3d2cbebcb7043',
                    '8dd4b32c84fc02ff3a9042320c1a452c2c583d1b0ebe7b059b13d799',
                    'c5452ec6e9ceb62ebcdec8fcd6fc3c8ed7ed5116628947e58c62725b' ]
        
        for fn in fns:
            assert os.path.exists( fn )

        for i, fn in enumerate(fns):
            hd = sha224(open(fn).read()).hexdigest()
            assert hd == digests[i]

        for fn in fns:
            os.remove( fn )
            
    def test_translate003(self):
        ipw = IPW('tests/testIPWs/in.0051')
        ipw.translate('tests/tmp/in.0051', multi=False)

        fns = [ 'tests/tmp/in.0051.tif']
        
        """
        f = open('tests/hash.txt', 'wb')
        for fn in fns:
            f.write(sha224(open(fn).read()).hexdigest())
            f.write('\r\n')
        """
        digests = [ '5476c846de4fd5066a7570975235f1a5a21e06004879b7fa96e81e31' ]
        
        for fn in fns:
            assert os.path.exists( fn )

        for i, fn in enumerate(fns):
            hd = sha224(open(fn).read()).hexdigest()
            assert hd == digests[i]

        for fn in fns:
            os.remove( fn )
            
    def test_translate004(self):
        ipw = IPW('tests/testIPWs/in.0051')
        ipw.translate('tests/tmp/in.0051', multi=False, writebands=[1,3,4])

        fns = [ 'tests/tmp/in.0051.tif']
        """
        f = open('tests/hash.txt', 'wb')
        for fn in fns:
            f.write(sha224(open(fn).read()).hexdigest())
            f.write('\r\n')
        """
        digests = [ '6846c31c58f7feddfd3b892635a09bb91ba983c3852e572b4212ce3a' ]
        
        for fn in fns:
            assert os.path.exists( fn )

        for i, fn in enumerate(fns):
            hd = sha224(open(fn).read()).hexdigest()
            assert hd == digests[i]

        for fn in fns:
            os.remove( fn )

class Test_hd5(unittest.TestCase):               
    def test_packToHD5(self):
        fname = 'tests/tmp/data.hd5'
        packToHd5(os.path.join('tests', 'testSet'), fname=fname)

        time.sleep(1)
        
        os.remove( fname )
        
def suite():
    return unittest.TestSuite((
            unittest.makeSuite(Test_readIPW),
            unittest.makeSuite(Test_translate),
            unittest.makeSuite(Test_hd5)
                              ))

if __name__ == "__main__":
    # run tests
    runner = unittest.TextTestRunner()
    runner.run(suite())
