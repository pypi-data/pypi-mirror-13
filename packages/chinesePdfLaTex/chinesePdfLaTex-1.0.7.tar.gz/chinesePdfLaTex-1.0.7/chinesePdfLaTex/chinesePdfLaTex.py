# coding=utf-8
'''
Created on Dec 25, 2015

@author: yangjie
'''
import os
import sys
from logger import pdfLogger
from chineseCom import CodeParse


class cplt():

    def __init__(self, fileName):
        self.fileName = fileName
        self.basePath = os.path.abspath('.')
        self.filePath = os.path.join(
            self.basePath, self.fileName).replace('\\', '/')
        self.fileExists = os.path.exists(self.filePath)

    def runThis(self):
        if self.fileExists:
            codeParse = CodeParse(self.filePath)
            codeParse.mainFunc()
        else:
            return
if __name__ == "__main__":
    cplt = cplt(sys.argv[1])
    cplt.runThis()
