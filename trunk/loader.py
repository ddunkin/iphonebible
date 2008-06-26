#!/usr/bin/env python

from google.appengine.ext import bulkload
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.ext import search

from datamodel import *

class WorkLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'Work',
                             [('osis_id', str),
                              ('title', str),
                              ])

class BookLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'Book',
                             [('_work_osis_id', str),
                              ('osis_id', str),
                              ('title', str),
                              ])

  def HandleEntity(self, entity):
    work = Work.gql('WHERE osis_id = :1', entity['_work_osis_id']).fetch(1)[0]
    entity['work'] = work.key()
    del entity['_work_osis_id']
    return entity


class ChapterLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'Chapter',
                             [('_work_osis_id', str),
                              ('_book_osis_id', str),
                              ('osis_id', str),
                              ('number', long),
                              ('title', str),
                              ])

  def HandleEntity(self, entity):
    work = Work.gql('WHERE osis_id = :1', entity['_work_osis_id']).fetch(1)[0]
    book = work.books.filter('osis_id =', entity['_book_osis_id']).fetch(1)[0]
    entity['book'] = book.key()
    del entity['_work_osis_id']
    del entity['_book_osis_id']
    return entity


class VerseLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'Verse',
                             [('_work_osis_id', str),
                              ('_book_osis_id', str),
                              ('_chapter_osis_id', str),
                              ('osis_id', str),
                              ('number', long),
                              ('text', str),
                              ])

  def HandleEntity(self, entity):
    work = Work.gql('WHERE osis_id = :1', entity['_work_osis_id']).fetch(1)[0]
    book = work.books.filter('osis_id =', entity['_book_osis_id']).fetch(1)[0]
    chapter = book.chapters.filter('osis_id =', entity['_chapter_osis_id']).fetch(1)[0]
    entity['chapter'] = chapter.key()
    del entity['_work_osis_id']
    del entity['_book_osis_id']
    del entity['_chapter_osis_id']
    return search.SearchableEntity(entity)


if __name__ == '__main__':
  bulkload.main(WorkLoader(), BookLoader(), ChapterLoader(), VerseLoader())

