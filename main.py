import sys, os

from lib import wk8
from lib.logger import getLogger
from lib.constants import *

L = getLogger("main")
w = wk8.Wenku8()

if not os.path.exists(OPT['outputDir']): os.makedirs(OPT['outputDir'])

for i in sys.argv[1:]:
  try:
    id = int(i)
    info = w.bookinfo(id)
    L.info("ID: %d, 标题: %s, 作者: %s, 简介: %s" % (id, info['name'], info['author'], info['brief']))
    w.get_book(id, info)
  except ValueError:
    L.info("搜索并下载: %s" % i)
    for b in w.search(i):
      L.info('搜索结果: %s，下载中.' % b['title'])
      info = w.bookinfo(b['bid'])
      w.get_book(b['bid'], info)
