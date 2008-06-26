#!/usr/bin/env python

import wsgiref.handlers
import os
import logging
from xml.dom.minidom import parseString

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

import datamodel


class UploadHandler(webapp.RequestHandler):

  def get(self):
    self.response.out.write("""
      <html>
        <body>
          <form action="/upload" enctype="multipart/form-data" method="post">
            <div><label>OSIS work:</label></div>
            <div><input type="file" name="osis"/></div>
            <div><input type="submit" value="Upload"></div>
          </form>
        </body>
      </html>""")

  def post(self):
    xml = self.request.get('osis')
    osis = parseString(xml)

    osis_text_node = osis.getElementsByTagName('osisText')[0]
    work_id = osis_text_node.getAttribute('osisIDWork')
    works = Work.gql('WHERE osis_id = :1', work_id).fetch(1)
    if len(works) == 1:
      work = works[0]
    else:
      work = Work(osis_id=work_id)
      # TODO: get title, etc.
      work.put()

    book_count = 0

    logging.info('Beginning import')
    for book_node in osis_text_node.getElementsByTagName('div'):
      book_count += 1
      book_id = book_node.getAttribute('osisID')
      if work.books.filter('osis_id = ', book_id).count() == 0:
        book_title = getText(book_node.getElementsByTagName('title')[0])
        logging.info('Creating book %s', book_title)
        book = Book(work=work, osis_id=book_id, title=book_title)
        book.put()

        chapter_i = 0
        for chapter_node in book_node.getElementsByTagName('chapter'):
          chapter_id = chapter_node.getAttribute('osisID')
          chapter_title = chapter_node.getAttribute('chapterTitle')
          chapter_i += 1
          logging.debug('Creating chapter %s', chapter_title)
          chapter = Chapter(book=book, osis_id=chapter_id, title=chapter_title, number=chapter_i)
          chapter.put()

          verse_i = 0
          for verse_node in chapter_node.getElementsByTagName('verse'):
            verse_id = verse_node.getAttribute('osisID')
            verse_i += 1
            verse = Verse(chapter=chapter, osis_id=verse_id, text=getText(verse_node), number=verse_i)
            verse.put()
    
    logging.info('Import complete')
    self.response.out.write('Imported %d books.' % book_count)

# returns all the text in the given element and its children
def getText(element):
  t = ''
  for n in element.childNodes:
    if n.nodeType == n.ELEMENT_NODE:
      t += getText(n)
    elif n.nodeType == n.TEXT_NODE:
      t += n.data
  return t

def main():
  application = webapp.WSGIApplication([('/admin/upload', UploadHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()

