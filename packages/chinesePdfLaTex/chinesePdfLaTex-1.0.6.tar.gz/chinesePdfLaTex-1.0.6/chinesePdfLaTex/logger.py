# coding=utf-8
'''
Created on Dec 25, 2015

@author: yangjie
'''
formatStr = "%(asctime)s [%(filename)s line %(lineno)d] [%(name)s %(levelname)s] %(message)s"
import logging
fmt = logging.Formatter(formatStr)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(fmt)

pdfLogger = logging.getLogger("ChinesePdfLaTex logger")
pdfLogger.setLevel(logging.INFO)
pdfLogger.addHandler(streamHandler)