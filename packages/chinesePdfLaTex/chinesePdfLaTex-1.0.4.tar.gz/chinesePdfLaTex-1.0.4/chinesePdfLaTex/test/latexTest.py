# coding=utf-8
'''
Created on Dec 25, 2015

@author: yangjie
'''
import os
import unittest2

from chineseCom import CodeParse


class LaTexTest(unittest2.TestCase):

    def setUp(self):
        self.codeParse = CodeParse("finalTest.tex")

    def tearDown(self):
        os.system(
            "rm finalTest.out finalTest.log finalTest.aux finalTest.pdf finalTest.toc")
        os.system("cp finalTest.bkp finalTest.tex")

    def test_1(self):
        self.codeParse.comPdfLaTex()

    def test_2(self):
        self.codeParse.mainFunc()
        os.system("cp finalTest.pdf ff.pdf")

if __name__ == "__main__":
    unittest2.main()
