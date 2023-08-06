"""
Unit testing for library functions.
Every method should start with "test". 
"""

import unittest
#import sys
#sys.path.append("..")
import file_parsing as fp
from decimal import *
import os

import pkg_resources
PATH = pkg_resources.resource_filename(__name__, 'test_hours_data/')


class test_file_parsing(unittest.TestCase):

    # Test total_hours function
    def test_hours_1(self):
        """
        Test 1 file with floats.
        """
        assert fp.total_hours([PATH + 'file1.vim']) == 16.75, "One file: test_hours_1 should return 16.75"

    def test_hours_2(self):
        """
        Test 1 file with integers, single hour and plural hours.
        """
        assert fp.total_hours([PATH + 'file2.vim']) == 17.0, "One file: test_hours_2 should return 17.0"

    def test_hours_3(self):
        """
        Test 2 files.
        """
        assert fp.total_hours([PATH + 'file1.vim', PATH + 'file2.vim']) == 33.75, "Two files: test_hours_3 should return 33.75"

    def test_hours_4(self):
        """
        Test 1 file with capital letters in the word "hours" and common typos.
        """
        assert fp.total_hours([PATH + 'file3.vim']) == 17.0, "One file: test_hours_4 should return 17.0"

    def test_hours_5(self):
        """
        Test 3 files.
        """
        assert fp.total_hours([PATH + 'file1.vim', PATH + 'file2.vim', PATH + 'file3.vim']) == 50.75, "Three files: test_hours_5 should return 50.75"

    def test_hours_6(self):
        """
        Test 1 file with inconsistent formatted floats.
        """
        assert fp.total_hours([PATH +'file4.vim']) == 1.5, "One file: test_hours_6 should return 1.5"

    # Test get_line_count function
    def test_get_line_count1(self):
        """
        Test line count for file1.vim.
        """
        line_count = fp.get_line_count(PATH + 'file1.vim')
        assert line_count == 30, "Should have 33 lines but has " + str(line_count)

    def test_get_line_count2(self):
        """
        Test line count for file2.vim.
        """
        line_count = fp.get_line_count(PATH + 'file2.vim')
        assert line_count == 26, "Should have 26 lines but has " + str(line_count)


    def test_get_line_count3(self):
        """
        Test line count for file3.vim.
        """
        line_count = fp.get_line_count(PATH + 'file3.vim')
        assert line_count == 26, "Should have 26 lines but has " + str(line_count)


    def test_get_line_count4(self):
        """
        Test line count for file4.vim.
        """
        line_count = fp.get_line_count(PATH + 'file4.vim')
        assert line_count == 16, "Should have 16 lines but has " + str(line_count)


    def test_get_line_count5(self):
        """
        Test line count for file5.txt, empty file with line breaks.
        """
        line_count = fp.get_line_count(PATH + 'file5.txt')
        assert line_count == 24, "Should have 24 lines but has " + str(line_count)

    # Test is_numeric function
    def test_is_numeric1(self):
        val1 = fp.is_numeric('0')
        val2 = fp.is_numeric('0.0')
        val3 = fp.is_numeric('700')
        val4 = fp.is_numeric('0.00000000001')
        val5 = fp.is_numeric(20)
        val6 = fp.is_numeric(20.5)

        val7 = fp.is_numeric('He who knows best knows how little he knows.')
        val8 = fp.is_numeric(True)
        val9 = fp.is_numeric(False)
        val10 = fp.is_numeric('seven')
        val11 = fp.is_numeric('3 2')
        val12 = fp.is_numeric(3 + 2)

        assert val1 == True, "Should be True, returned " + str(val1)
        assert val2 == True, "Should be True, returned " + str(val2)
        assert val3 == True, "Should be True, returned " + str(val3)
        assert val4 == True, "Should be True, returned " + str(val4)
        assert val5 == True, "Should be True, returned " + str(val5)
        assert val6 == True, "Should be True, returned " + str(val6)

        assert val7 == False, "Should be False, returned " + str(val7)
        assert val8 == True, "Should be True, returned " + str(val8)
        assert val9 == True, "Should be True, returned " + str(val9)
        assert val10 == False, "Should be False, returned " + str(val10)
        assert val11 == False, "Should be False, returned " + str(val11)
        assert val12 == True, "Should be True, returned " + str(val12)

    
    def test_is_number_of_some_sort(self):
        val1 = fp.is_number_of_some_sort(4)   
        val2 = fp.is_number_of_some_sort(4.4)   
        val3 = fp.is_number_of_some_sort(Decimal(4.4))
        val4 = fp.is_number_of_some_sort(Decimal(4))
        val5 = fp.is_number_of_some_sort('4')
        val6 = fp.is_number_of_some_sort('4.4')
        val7 = fp.is_number_of_some_sort('')
        val8 = fp.is_number_of_some_sort('Son of Mogh')


        self.assertEqual(val1, True, 'Should be True, returned False')
        self.assertEqual(val2, True, 'Should be True, returned False')
        self.assertEqual(val3, True, 'Should be True, returned False')
        self.assertEqual(val4, True, 'Should be True, returned False')
        self.assertEqual(val5, False, 'Should be False, returned True')
        self.assertEqual(val6, False, 'Should be False, returned True')
        self.assertEqual(val7, False, 'Should be False, returned True')
        self.assertEqual(val8, False, 'Should be False, returned True')



# Run all tests
#if __name__ == "__main__":
#    unittest.main()
