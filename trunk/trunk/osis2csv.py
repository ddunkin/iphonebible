#!/usr/bin/env python

import sys
import logging
from xml.dom.minidom import parse
import csv
from unicodeCsv import UnicodeWriter
from google.appengine.ext.db import Key

# returns all the text in the given element and its children
def getText(element):
  t = ''
  for n in element.childNodes:
    if n.nodeType == n.ELEMENT_NODE:
      t += getText(n)
    elif n.nodeType == n.TEXT_NODE:
      t += n.data
  return t

def createCSV(osis_xml_file):
  osis = parse(osis_xml_file)

  works_writer = csv.writer(open('works.csv', 'wb'))
  books_writer = csv.writer(open('books.csv', 'wb'))
  chapters_writer = csv.writer(open('chapters.csv', 'wb'))
  verses_writer = csv.writer(open('verses.csv', 'wb'))

  for osis_text_node in osis.getElementsByTagName('osisText'):
    work_id = osis_text_node.getAttribute('osisIDWork')
    work_title = work_id # TODO: get title
    works_writer.writerow([work_id, work_title])

    book_count = 0

    logging.info('Beginning import')
    for book_node in osis_text_node.getElementsByTagName('div'):
      book_count += 1
      book_id = book_node.getAttribute('osisID')
      book_title = getText(book_node.getElementsByTagName('title')[0]).encode('ascii', 'xmlcharrefreplace')
      logging.info('Creating book %s', book_title)
      books_writer.writerow([work_id, book_id, book_title])

      chapter_i = 0
      for chapter_node in book_node.getElementsByTagName('chapter'):
        chapter_id = chapter_node.getAttribute('osisID')
        chapter_title = chapter_node.getAttribute('chapterTitle').encode('ascii', 'xmlcharrefreplace')
        chapter_i += 1
        logging.debug('Creating chapter %s', chapter_title)
        chapters_writer.writerow([work_id, book_id, chapter_id, str(chapter_i), chapter_title])

        verse_i = 0
        for verse_node in chapter_node.getElementsByTagName('verse'):
          verse_id = verse_node.getAttribute('osisID')
          verse_i += 1
          verse_text = getText(verse_node).encode('ascii', 'xmlcharrefreplace')
          verses_writer.writerow([work_id, book_id, chapter_id, verse_id, str(verse_i), verse_text])
    
  logging.info('Import complete')


if __name__ == '__main__':
  if len(sys.argv) == 2:
    createCSV(sys.argv[1])
  else:
    print 'Usage: osis2csv.py osisFile.xml'
