"""
Unit testing for library functions.
Every method should start with "test". 
"""

import unittest
#import sys
#sys.path.append("..")
#import convert_php as cp

#class test_list_manipulation(unittest.TestCase):
    # 
#    def test_unserialize_php_array(self):
#        print
#        unserialize = cp.ConvertPHP()
#        unserialize.translate_array('a:4:{i:0;a:7:{s:2:"id";i:2386211;s:6:"status";s:9:"AVAILABLE";s:8:"location";s:18:"Crerar, Bookstacks";s:7:"reserve";s:1:"N";s:10:"callnumber";s:6:" Q1.N2";s:6:"foobar";a:4:{s:3:"one";i:1;s:3:"two";i:2;s:5:"three";i:3;s:4:"four";i:4;}s:12:"availability";b:1;}i:1;a:8:{s:2:"id";i:2386211;s:6:"status";s:7:"MISSING";s:4:"test";a:5:{i:0;i:1;i:1;i:2;i:2;i:3;i:3;i:4;i:4;i:5;}s:8:"location";s:18:"Crerar, Bookstacks";s:7:"reserve";s:1:"N";s:8:"testnull";N;s:10:"callnumber";s:6:" Q1.N2";s:12:"availability";b:0;}i:2;a:6:{s:2:"id";i:2386211;s:6:"status";s:9:"AVAILABLE";s:8:"location";s:18:"Crerar, Bookstacks";s:7:"reserve";s:1:"N";s:10:"callnumber";s:6:" Q1.N2";s:12:"availability";b:1;}i:3;a:6:{s:2:"id";i:2386211;s:6:"status";s:9:"AVAILABLE";s:8:"location";s:38:"Special Collections, Crerar Rare Books";s:7:"reserve";s:1:"N";s:10:"callnumber";s:6:" Q1.N2";s:12:"availability";b:1;}}', 'php')

#lm.unserialize_php_array('a:4:{i:0;a:7:{s:2:"id";i:2386211;s:6:"status";s:9:"AVAILABLE";s:8:"location";s:18:"Crerar, Bookstacks";s:7:"reserve";s:1:"N";s:10:"callnumber";s:6:" Q1.N2";s:6:"foobar";a:4:{s:3:"one";i:1;s:3:"two";i:2;s:5:"three";i:3;s:4:"four";i:4;}s:12:"availability";b:1;}i:1;a:8:{s:2:"id";i:2386211;s:6:"status";s:7:"MISSING";s:4:"test";a:5:{i:0;i:1;i:1;i:2;i:2;i:3;i:3;i:4;i:4;i:5;}s:8:"location";s:18:"Crerar, Bookstacks";s:7:"reserve";s:1:"N";s:8:"testnull";N;s:10:"callnumber";s:6:" Q1.N2";s:12:"availability";b:0;}i:2;a:6:{s:2:"id";i:2386211;s:6:"status";s:9:"AVAILABLE";s:8:"location";s:18:"Crerar, Bookstacks";s:7:"reserve";s:1:"N";s:10:"callnumber";s:6:" Q1.N2";s:12:"availability";b:1;}i:3;a:6:{s:2:"id";i:2386211;s:6:"status";s:9:"AVAILABLE";s:8:"location";s:38:"Special Collections, Crerar Rare Books";s:7:"reserve";s:1:"N";s:10:"callnumber";s:6:" Q1.N2";s:12:"availability";b:1;}}', 'python')


# Run all tests
#if __name__ == "__main__":
#    unittest.main()
