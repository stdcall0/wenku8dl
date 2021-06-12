from ebooklib import epub
import mime, threading
from lib.constants import *

class Book:
  def __init__(self, meta: dict[str], book_id, title, chapter_cnt):
    self.book = epub.EpubBook()
    self.book.set_identifier(meta['identifier'])
    self.book.set_title(meta['title'])
    self.book.set_language(meta['language'])
    if 'creator' in meta: self.book.add_author(meta['creator'])
    if options['moreAuthor'] and 'contributor' in meta: self.book.add_author(meta['contributor'], None, None, 'contributor')
    if options['moreAuthor'] and 'publisher' in meta: self.book.add_author(meta['publisher'], None, None, 'publisher')
    if options['moreMeta'] and 'date' in meta: self.book.add_metadata('DC', 'date', meta['date'])
    if options['moreMeta'] and 'description' in meta: self.book.add_metadata('DC', 'description', meta['description'])
    self.css = self.book.add_item(epub.EpubItem(uid="style", file_name="style/style.css", media_type="text/css", content=CSS))
    self.chapters = [None for i in range(0, chapter_cnt)]
    self.book_id = book_id
    self.lock = threading.Lock()
    self.spine = ['cover', self.addChapter(-1, title, INTRO % (title, book_id), False), 'nav']
  
  def addImage(self, filename, content):
    img = epub.EpubItem(
      file_name="images/%s" % filename,
      media_type=mime.Types.of(filename)[0].content_type,
      content=content
    )
    self.lock.acquire()
    self.book.add_item(img)
    self.lock.release()

  def addChapter(self, index, title, content, addToList = True):
    page = epub.EpubHtml(title=title, file_name='%s.xhtml' % (index + 1), content=(HTML % (title, content)).encode("utf-8"), lang="zh")
    page.add_item(self.css)
    self.lock.acquire()
    self.book.add_item(page)
    self.lock.release()
    if addToList: self.chapters[index] = page
    return page

  def finalize(self, filename: str, cover_data, cover_ext: str):
    toc = [epub.Link('0.xhtml', self.book.title, 'title')]
    for chapter in self.chapters:
      if chapter is None:
        continue
      toc.append(chapter)
      self.spine.append(chapter)
    self.book.set_cover('cover' + cover_ext, cover_data)
    self.book.toc = toc
    self.book.spine = self.spine

    self.book.add_item(epub.EpubNcx())
    self.book.add_item(epub.EpubNav())

    epub.write_epub(filename, self.book)
    return True
