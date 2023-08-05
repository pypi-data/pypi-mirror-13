# coding=utf-8
'''
Created on Dec 23, 2015

@author: yangjie
'''
import re
from logger import pdfLogger


class IndexParse():
    """
    处理latex的书签
    """
    patternBOOKMARK = "(\\\\BOOKMARK) \[(.*)\]\[(.*)\]\{(.*)\}\{(.*)\}\{(.*)\}([%] [0-9]*)?"
    regexBOOKMARK = re.compile(patternBOOKMARK)
    formatBOOKMARD = "%s [%s][%s]{%s}{%s}{%s}%s"
    unicodePrefix = "\\376\\377"
    contentIndex = 4

    def __init__(self, filePath):
        self.filePath = filePath
        pdfLogger.info("create file parser: DONE")
        pass

    def mainFunc(self):
        """
        将*.out文件按行分解为列表 每个列表按正则表达式分解为列表
        @return: 分解后的字符串
        """
        dataList = self.loadOutFile()
        splitList = self.splitLine(dataList)
        resList = []
        for index, line in enumerate(splitList):
            splitList[index][self.contentIndex] = self.convertStrToASCIIStr(
                line[self.contentIndex])
            resList.append(self.formatBOOKMARD % tuple(splitList[index]))
        self.writeOutFile(resList)
        pdfLogger.info("job done")
        return

    def writeOutFile(self, resList):
        with open(self.filePath, mode="w", encoding="utf-8")as outFile:
            for line in resList:
                outFile.write(line + "\n")
        pdfLogger.info("write " + self.filePath + " file: DONE")

    def loadOutFile(self):
        """
        读取*.out文件 此文件为latex的书签文件
        @return: 按行分开 返回列表
        """
        with open(self.filePath, mode="r", encoding="utf-8") as outFile:
            # TODO
            dataTem = outFile.read()
        dataList = dataTem.split(sep="\n")
        pdfLogger.info("read " + self.filePath + " file: DONE")
        return dataList

    def splitLine(self, dataList):
        """
        """
        resList = []
        for line in dataList:
            try:
                temSearch = self.regexBOOKMARK.search(line)
                temList = list(temSearch.groups())
                resList.append(temList)
            except Exception:
                pdfLogger.error("illegal line: " + line)
        pdfLogger.info("split line: DONE")
        return resList

    def convertStrToASCIIStr(self, aimStr):
        """
        将字符串转换为八进制数字串 并补码 \\376 \\377
        @return: 八进制数字串 字符串形式
        """
        octList = [self.convertCharToASCIIStr(item) for item in aimStr]
        octList.insert(0, self.unicodePrefix)
        octList = "".join(octList)
        return octList

    def convertCharToASCIIStr(self, aimChar):
        """
        将一个字符截取为两个字节
        @return: 型为 \\000 的八进制数字
        """
        charOrd = ord(aimChar)
        firstByte = "\\%03o" % ((charOrd >> 8) & 0xFF)
        """
        截取后八位前的内容
        """
        secondByte = "\\%03o" % (charOrd & 0xFF)
        """
        截取后八位
        """
        octStr = "".join((firstByte, secondByte))
        pdfLogger.info("convert string to ascii: DONE")
        return octStr
