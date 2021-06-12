import sys, os, re, io, threading, copy, getopt
import unittest
from logging import getLogger

from lib import logger, wk8

logger.enable()
L = getLogger("test")

class Wenku8TestCase(unittest.TestCase):
  def setUp(self):
    self.w = wk8.Wenku8()
  def test_login(self):
    L.info("测试: 登陆")
    self.assertTrue(self.w.login(), 'failed to login')
  def test_search(self):
    L.info("测试: 搜索")
    self.assertGreater(len(self.w.search("这件事")), 0, 'failed to search')
  def test_bookinfo(self):
    L.info("测试: 图书信息")
    self.assertIsNotNone(self.w.bookinfo(2580), 'failed to get bookinfo')
  def test_getbook(self):
    L.info("测试: 图书下载")
    self.assertTrue(self.w.get_book(2580, self.w.bookinfo(2580)), 'failed to get book')

if __name__ == "__main__":
  print("请使用 python -m unittest 进行测试。")
