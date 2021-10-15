import os, re, threading

import bs4, requests as R
from bs4 import BeautifulSoup as Soup

from lib import epub
from lib.logger import getLogger
from lib.constants import *

def req(method : str, url : str, headers : dict = {}, payload : dict = {}, cookies = None):
  return R.request(method, url, headers = headers | USER_AGENT, data = payload, cookies = cookies)

def reqr(soup : bool, method : str, url : str, headers : dict = {}, payload : dict = {}, cookies = None):
  res = R.request(method, url, headers = headers | USER_AGENT, data = payload, cookies = cookies)
  html = res.content.decode("gbk", errors="ignore")
  if soup: return res, html, Soup(html, PARSER)
  else: return res, html

mxLen = 0
def progressBar(pre, x, y):
  global mxLen
  print(' '*(mxLen * 2), end='\r')
  CNT = 20
  spc = CNT * x // y
  p = "%s: %d/%d [%s%s]" % (pre, x,y, "=" * spc, "." * (CNT - spc))
  mxLen = max(mxLen, len(p))
  print(p, end='\r')

class Wenku8:
  def __init__(self):
    self.cookies = ""
    self.cookie_jar = None
    self.image_count = 0
    self.image_total = 0
    self.book = None
    self.L = getLogger("wenku8")

  def login(self, username= OPT['account'][0], password= OPT['account'][1]):
    self.L.debug("正在登陆: 使用账号 %s 密码 %s" % (username, password))
    data = {'action': 'login', 'jumpurl': '', 'username': username, 'password': password}
    res, html = reqr(False, 'post', API['login'], CONTENT_TYPES['post'], data)
    if '登录成功' not in html:
      self.L.error("登陆失败: 返回内容 %s" % html)
      return False
    self.cookies = ''
    for key, value in res.cookies.items():
      self.cookies += "%s=%s;" % (key, value)
    self.L.debug("登陆成功。Cookie: %s" % self.cookies)
    self.cookie_jar = res.cookies
    return True

  def is_login(self):
    return len(self.cookies) != 0 and self.cookie_jar is not None

  def search(self, key: str):
    if not self.is_login():
      self.login()
      if not self.is_login():
        self.L.error("登陆失败，无法搜索。")
        return False
    m1 = self.search_one(API["search1"], key)
    m2 = self.search_one(API["search2"], key)
    self.L.debug("搜索 %s: 结果共 %d 条，API 1: %d, API 2: %d" % (key, len(m1) + len(m2), len(m1), len(m2)))
    return m1 + m2

  def search_one(self, API: str, key: str):
    if not self.is_login():
      return []
    headers = {'Cookie': self.cookies}
    encodings = key.encode('gbk').hex().upper()
    key_arg = ''
    for i in range(0, len(encodings), 2):
      key_arg += "%%%s%s" % (encodings[i], encodings[i + 1])
    self.L.debug("搜索: URL: %s" % API % key_arg)

    res, html, soup = reqr(True, "get", API % key_arg, headers, {}, self.cookie_jar)

    if '推一下' in html:
      title = soup.find_all('b')[1].get_text()
      bid = ''
      for n in re.findall(r'\d', res.url)[1:]:
        bid = bid + n
      bid = int(bid)
      try:
        cover = soup.find_all('img')[1].get_attribute_list('src')[0]
      except IndexError:
        cover = None
      try:
        status = soup.find_all('table')[0].find_all('tr')[2].get_text().replace('\n', ' ')
      except IndexError:
        status = None
      try:
        brief = soup.find_all('table')[2].find_all('td')[1].find_all('span')[4].get_text()
      except IndexError:
        spans = soup.find_all('span')
        for i in range(len(spans)):
          if '内容简介' in spans[i].get_text():
            brief = spans[i + 1].get_text()
      book = {
        'title': title, 'bid': bid, 'cover': cover, 'status': status, 'brief': brief
      }
      self.L.debug("搜索: 书名 %s, ID %d, 封面链接 %s, 状态 %s, 简介 %s" % (title, bid, cover, status, brief))
      return [book, ]

    td = soup.find('td')
    if td is None: return []
    books = []
    for content in td.children:
      if not isinstance(content, bs4.element.Tag):
        continue
      title = content.find_all('a')[1].get_text()
      url = content.find_all('a')[1].get_attribute_list('href')[0]
      numbers = re.findall(r'\d', url)[1:]
      bid = ''
      for n in numbers:
        bid = bid + n
      bid = int(bid)
      cover = content.find_all('img')[0].get_attribute_list('src')[0]
      status = content.find_all('p')[0].get_text()
      brief = content.find_all('p')[1].get_text()[3:]
      book = {
        'title': title, 'bid': bid, 'cover': cover, 'status': status, 'brief': brief
      }
      self.L.debug("搜索: 书名 %s, ID %d, 封面链接 %s, 状态 %s, 简介 %s" % (title, bid, cover, status, brief))
      books.append(book)
    return books

  def bookinfo(self, book_id: int):
    url = "%s%s" % (API["book"] % (("%04d" % book_id)[0], book_id), "index.htm")
    self.L.debug("图书信息: %d: URL %s" % (book_id, url))
    __, html, soup = reqr(True, "get", url)
    table = soup.select('table')
    if len(table) == 0:
      self.L.error("图书信息: 无法获取，更多信息请打开调试模式")
      self.L.debug("返回页面: %s" % html)
      return None

    table = table[0]
    if len(soup.select("#title")) == 0:
      self.L.error("图书信息: 该书不存在。")
      return None

    title = soup.select("#title")[0].get_text()
    author = soup.select("#info")[0].get_text().split('作者：')[-1]
    url_cover = API["img"] % (("%04d" % book_id)[0], book_id, book_id)

    brief = ''
    url = API["info"] % (book_id)
    __, html, soup = reqr(True, "get", url)
    update = ''
    for td in soup.find_all('td'):
      if '最后更新' in td.get_text():
        update = td.get_text()[5:]
    iscopyright = '因版权问题，文库不再提供该小说的在线阅读与下载服务！' not in soup.get_text()
    spans = soup.select('span')
    for i in range(len(spans)):
      span = spans[i]
      if '内容简介' in span.get_text():
        brief = spans[i + 1].get_text()
    self.L.debug("图书信息: %d: 标题 %s, 作者 %s, 简介 %s, 封面链接 %s, 版权 %s, 最后更新 %s" % (book_id, title, author, brief, url_cover, str(iscopyright), update))
    return {
      "id": book_id,
      "name": title,
      "author": author,
      "brief": brief,
      "cover": url_cover,
      'copyright': iscopyright,
      'update': update
    }

  def get_page(self, url_page: str, title: str = ''):
    __, html = reqr(False, 'get', url_page)
    html = re.sub(r"\[sup\](.{1,50})\[\/sup\]", r"<sup>\1</sup>", html)
    soup = Soup(html, PARSER)
    content = soup.select('#content')[0]
    [s.extract() for s in content("ul")] # 去除 <ul>
    return "<h1>%s</h1>%s" % (title, content.prettify())

  def fetch_img(self, url_img: str):
    self.L.debug("图片链接为: %s" % url_img)
    data_img = req('get', url_img).content
    filename = os.path.basename(url_img)
    self.book.addImage(filename, data_img)
    self.image_count += 1
    progressBar(self.chapter_name + " 插图", self.image_count, self.image_total)
    return True

  def isImg(self, x):
    for i in IMG_PREFIXES:
      if i in x: return True
    return False

  def fetch_chapter(self, a, order: int):
    title_page = a.get_text()
    url_page = "%s%s" % (API['book'] % (("%04d" % self.book.book_id)[0], self.book.book_id), a.get('href'))
    self.L.debug("%s下载: %s: %s - %s" % ("插图" if title_page == "插图" else "章节", title_page, a.get('href'), url_page))
    soup = Soup(self.get_page(url_page, title=title_page), PARSER)
    imgcontent = soup.select(".imagecontent")

    if not OPT['noImage']:
      if len(imgcontent) > 0:
        self.L.debug("图书下载: %s: 可能的封面: %s" % (title_page, imgcontent[0].get("src")))
        self.cover_frombook = imgcontent[0].get("src")
      if OPT['downloadImage']:
        img_pool = []
        imgcontent = [i for i in filter(lambda x: self.isImg(x.get("src")), imgcontent)]
        self.image_total += len(imgcontent)
        for img in imgcontent:
          url_img = img.get("src")
          self.L.debug("%s下载: 图片: %s in %s" % ("插图" if title_page == "插图" else "章节", url_img, title_page))
          img["src"] = "images/" + os.path.basename(img.get("src"))
          if img.parent.name == 'a':
            img.parent.unwrap()
          th = threading.Thread(target=self.fetch_img, args=(url_img,), daemon=True)
          if OPT['imgPool']: th.start()
          img_pool.append(th)

        for it in img_pool: # no multi thread, one by one is significantly quicker
          if not OPT['imgPool']: it.start()
          it.join()
      else:
        for img in imgcontent:
          if img.parent.name == 'a':
            img.parent.unwrap()
    else:
      for i in imgcontent:
        if i.parent.name == 'a':
          i.parent.unwrap()
        i.extract()

    self.chapter_count += 1
    progressBar(self.chapter_name, self.chapter_count, self.chapter_total)
    self.book.addChapter(order, title_page, soup.prettify())

  def get_volume(self, book_id: int, book_info: dict[str], volume_index: int, hrefs: list[str], sub_title: str, base_title: str, author: str, backup_cover: str):
    self.cover_frombook = None
    self.book = epub.Book({
      "identifier": "%d-%.3d" % (book_id, volume_index),
      "title": "%s %s" % (base_title, sub_title),
      "language": "zh",
      "creator": author,
      "contributor": "wenku8toepub",
      "publisher": "wenku8",
      "date": book_info["update"],
      "description": book_info["brief"]
    }, book_id, "%s %s" % (base_title, sub_title), len(hrefs))
    pool = []
    self.image_count = self.image_total = self.chapter_count = 0
    self.chapter_name = "%s %s" % (base_title, sub_title)
    self.chapter_total = len(hrefs)
    for index, href in enumerate(hrefs):
      th = threading.Thread(target=self.fetch_chapter, args=(href, index), daemon=True)
      if OPT['chapterPool']: th.start()
      pool.append(th)
    for th in pool:
      if not OPT['chapterPool']: th.start()
      th.join()

    fn = OPT['outputDir'] + "\\[%s][%s][%.3d]%s.epub" % (author, base_title, volume_index + 1, sub_title)
    if OPT['noImage'] or not OPT['downloadCover']:
      # self.L.info("图书分卷 %s %s: 保存到 %s" % (base_title, sub_title, fn))
      return self.book.finalize(fn, None, None)
    else:
      if self.cover_frombook is None:
        cover_file = backup_cover
      else:
        cover_file = self.cover_frombook
      cover_data = req('get', cover_file).content
      cover_data = b""
      __, cover_ext = os.path.splitext(cover_file)
      self.L.debug("图书分卷 %s %s: 采用封面 [%d]: %s" % (base_title, sub_title, len(cover_data), cover_file))
      # self.L.info("图书分卷 %s %s: 保存到 %s" % (base_title, sub_title, fn))
      return self.book.finalize(fn, cover_data, cover_ext)

  def get_book(self, book_id: int, book_info: dict[str]):
    book_url = "%s%s" % (API['book'] % (("%04d" % book_id)[0], book_id), "index.htm")
    self.L.debug("图书下载: %d: URL %s" % (book_id, book_url))
    __, html, soup = reqr(True, 'get', book_url)
    table = soup.select('table')
    if len(table) == 0:
      self.L.error("图书下载: %d: 找不到内容，返回页面为 %s" % html)
      return False

    table = table[0]
    if len(soup.select("#title")) == 0:
      self.L.error("图书下载: %d: 找不到标题，返回页面为 %s" % html)
      return

    title = soup.select("#title")[0].get_text()
    author = soup.select("#info")[0].get_text().split('作者：')[-1]
    url_cover = API['img'] % (("%04d" % book_id)[0], book_id, book_id)
    if OPT['simplifyTitle']:
      title = re.sub(r"\(.*?\)", "", title)
      book_info['name'] = re.sub(r"\(.*?\)", "", book_info['name'])

    self.L.debug('图书下载: %d: 标题 %s, 作者 %s' % (book_id, title, author))

    iscopyright = '因版权问题，文库不再提供该小说的在线阅读与下载服务！' not in soup.get_text()
    if not iscopyright:
      self.L.error('图书下载: %s: 没有版权，下载中断。', title)
      return False

    A = [i for i in filter(lambda x : x.get_text().encode() != b'\xc2\xa0', table.select('td'))]
    trs = [i[0] for i in filter(lambda x : len(x[1].select('a')) == 0, enumerate(A))]
    self.L.debug("分卷数: %d 页面数: %d" % (len(A), len(trs)))

    self.L.info('图书下载: %d [%s] %s 共 %d 分卷' % (book_id, author, title, len(trs)))

    for ind, tr in enumerate(trs):
      subtitle = A[tr].get_text()
      self.L.debug("分卷 %d 页面范围 %d - %d" % (ind + 1, tr+2, len(A) if ind == len(trs) - 1 else trs[ind + 1]))
      hrefs = [i.select('a')[0] for i in (A[tr+1:] if ind == len(trs) - 1 else A[tr+1:trs[ind+1]])]
      self.get_volume(book_id, book_info, ind, hrefs, subtitle, title, author, url_cover)
    return True
