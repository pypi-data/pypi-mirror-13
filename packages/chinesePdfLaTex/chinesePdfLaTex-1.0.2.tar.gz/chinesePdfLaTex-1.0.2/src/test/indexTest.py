# coding=utf-8
'''
Created on Dec 23, 2015

@author: yangjie
'''
import os
import unittest2

from chineseIndex import IndexParse


class IndexTest(unittest2.TestCase):
    filePath = "bookMarkTest.out"

    def setUp(self):
        self.indexParse = IndexParse(self.filePath)

    def tearDown(self):
        os.system("rm bookMarkTest.out")
        os.system("cp bookMarkTest.bkp bookMarkTest.out")

    def test_1(self):
        octChar = self.indexParse.convertCharToASCIIStr("a")
        self.assertEqual(octChar, "\\000\\141")

    def test_2(self):
        octChar = self.indexParse.convertCharToASCIIStr("啊")
        self.assertEqual(octChar, "\\125\\112")

    def test_3(self):
        octStr = self.indexParse.convertStrToASCIIStr("I 正文aaaa")
        self.assertEqual(
            octStr, "\\376\\377\\000\\111\\000\\040\\153\\143\\145\\207\\000\\141\\000\\141\\000\\141\\000\\141")

    def test_4(self):
        octStr = self.indexParse.convertStrToASCIIStr("I正文aaaa")
        self.assertEqual(
            octStr, "\\376\\377\\000\\111\\153\\143\\145\\207\\000\\141\\000\\141\\000\\141\\000\\141")

    def test_5(self):
        dataList = self.indexParse.loadOutFile()
        exList = ['\\BOOKMARK [-1][-]{part.1}{I 部分测试}{}% 1',
                  '\\BOOKMARK [0][-]{chapter.1}{章测试}{part.1}% 2']
        self.assertEqual(dataList, exList)

    def test_6(self):
        self.indexParse.mainFunc()
        with open(self.filePath) as outFile:
            res = outFile.read()

    def test_7(self):
        os.system("python3 ../ChinesePdfLaTex.py bookMarkTest.out")


if __name__ == "__main__":
    unittest2.main()
