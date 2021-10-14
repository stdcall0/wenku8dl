import mime, threading, datetime
from ebooklib import epub

from lib.logger import getLogger
from lib.constants import *

L = getLogger("epub")

class Book:
  def __init__(self, meta: dict[str], book_id, title, chapter_cnt):
    self.book = epub.EpubBook()
    self.book.set_identifier(meta['identifier'])
    self.book.set_title(meta['title'])
    self.book.set_language(meta['language'])
    if 'creator' in meta: self.book.add_author(meta['creator'], None, 'aut', 'creator')
    if OPT['moreAuthor'] and 'contributor' in meta: self.book.add_metadata('DC', 'contributor', meta['contributor'])
    if OPT['moreAuthor'] and 'publisher' in meta: self.book.add_metadata('DC', 'publisher', meta['publisher'])
    if OPT['moreMeta'] and 'date' in meta: self.book.add_metadata('DC', 'date', meta['date'])
    if OPT['moreMeta'] and 'description' in meta: self.book.add_metadata('DC', 'description', meta['description'])
    self.book.add_metadata(None, 'meta', datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z', {'property': 'dcterms:modified'})
    self.css = self.book.add_item(epub.EpubItem(uid="style", file_name="style/style.css", media_type="text/css", content=CSS))
    self.chapters = [None for i in range(0, chapter_cnt)]
    self.book_id = book_id
    self.lock = threading.Lock()
    self.titlePage = self.addChapter(-1, "标题", INTRO(title, meta['creator'], book_id), "title")
    self.makerPage = self.addChapter(-1, "制作信息", MAKERINFO(meta['creator']), "makerinfo")

  def addImage(self, filename, content):
    img = epub.EpubItem(
      file_name= "images/%s" % filename,
      media_type= mime.Types.of(filename)[0].content_type,
      content= content
    )
    self.lock.acquire()
    self.book.add_item(img)
    self.lock.release()

  def addChapter(self, index, title, content, spec = None):
    item_id = "item-%.4d" % (index + 1) if spec is None else "item-" + spec
    file_name= '%.4d.xhtml' % (index + 1) if spec is None else spec + ".xhtml"
    page = epub.EpubItem(
      uid= item_id,
      file_name= file_name,
      media_type= 'application/xhtml+xml',
      content= HTML(title, content).encode("utf-8")
    )
    self.lock.acquire()
    self.book.add_item(page)
    self.lock.release()
    if spec is None: self.chapters[index] = (page, title, file_name, item_id)
    return page

  def finalize(self, filename: str, cover_data, cover_ext: str):
    has_cover = cover_data is not None
    if has_cover:
      self.book.set_cover('images/cover' + cover_ext, cover_data, False)
      self.coverPage = self.addChapter(-1, "封面", COVER('images/cover' + cover_ext), "cover")
    else:
      self.coverPage = None

    toc = ([ENTRY('cover.xhtml', -1, '封面')] if has_cover else []) + [ENTRY('title.xhtml', -1, '标题'), ENTRY('makerinfo.xhtml', -1, '制作信息'), ENTRY('contents.xhtml', -1, '目录')]

    ch = [i for i in filter(lambda x: x is not None, self.chapters)]
    for id, chapter in enumerate(ch):
      toc.append(ENTRY(chapter[2], id + 1, chapter[1]))

    self.tocPage = self.addChapter(-1, "目录", TOC("".join(toc)), "contents")

    LINK = lambda id, text: epub.Link(id + '.xhtml', text, 'item-' + id)
    extra_spine = [i[0] for i in ch]
    extra_toc = [epub.Link(i[2], i[1], i[3]) for i in ch]
    self.book.toc = ([LINK('cover', '封面')] if has_cover else []) + [LINK('title', '标题'), LINK('makerinfo', '制作信息'), LINK('contents', '目录')] + extra_toc
    self.book.spine = ([self.coverPage] if has_cover else []) + [self.titlePage, self.makerPage, self.tocPage] + extra_spine

    self.book.add_item(epub.EpubNcx())
    self.book.add_item(epub.EpubNav())

    epub.write_epub(filename, self.book)
    return True
