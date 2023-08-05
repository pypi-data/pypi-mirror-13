# coding=utf-8
'''
Created on Dec 25, 2015

@author: yangjie
'''
import os
from logger import pdfLogger
from chineseIndex import IndexParse


class CodeParse():

    def __init__(self, filePath):
        self.filePath = filePath
        self.outfilePath = filePath[:-3] + "out"
        self.indexParse = IndexParse(self.outfilePath)

    def comPdfLaTex(self):
        try:
            os.system("pdflatex " + self.filePath)
            pdfLogger.info("pdfLaTex: DONE")
        except Exception as error:
            pdfLogger.critical(error)

    def comIndex(self):
        try:
            self.indexParse.mainFunc()
        except Exception as error:
            pdfLogger.critical(error)

    def mainFunc(self):
        self.comPdfLaTex()
        self.comIndex()
        self.comPdfLaTex()
