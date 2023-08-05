# coding=utf-8
'''
Created on Dec 25, 2015

@author: yangjie
'''
# coding=utf-8
'''
Created on Dec 25, 2015

@author: yangjie
'''
import os
import unittest2


class MainTest(unittest2.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        os.system(
            "rm finalTest.out finalTest.log finalTest.aux finalTest.pdf finalTest.toc")
        os.system("cp finalTest.bkp finalTest.tex")

    def test_1(self):
        os.system("python3 ../chinesePdfLaTex.py finalTest.tex")
        os.system("cp finalTest.pdf ff.pdf")

if __name__ == "__main__":
    unittest2.main()
