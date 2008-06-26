#!/usr/bin/env python

import wsgiref.handlers
import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext import search
from google.appengine.ext.webapp import template
from google.appengine.api import users
from django.utils import simplejson

from datamodel import *

class MainHandler(webapp.RequestHandler):

  def get(self):
    books = Book.all()
    user = users.get_current_user()
    template_values = {
      'books': books,
      'user': user,
      'login_url': users.create_login_url('/'),
      'logout_url': users.create_logout_url('/')
    }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))


class BookHandler(webapp.RequestHandler):

  def get(self, work_id, book_id):
    work = Work.gql('WHERE osis_id = :1', work_id).get()
    book = work.books.filter('osis_id = ', book_id).get()
    template_values = {
      'work': work,
      'book': book,
      'chapters': book.chapters
    }
    path = os.path.join(os.path.dirname(__file__), 'book.html')
    self.response.out.write(template.render(path, template_values))


class ChapterHandler(webapp.RequestHandler):

  def get(self, work_id, book_id, chapter_number, verse_number = 1):
    user = users.get_current_user()
    work = Work.gql('WHERE osis_id = :1', work_id).get()
    book = work.books.filter('osis_id = ', book_id).get()
    chapter = book.chapters.filter('number = ', long(chapter_number)).get()
    verses = chapter.verses.fetch(100) # fetch because bookmarks don't work otherwise, TODO: figure out why
    bookmarks = []
    for verse in verses:
      verse._bookmark = verse.bookmarks.filter('user =', user).get()
    template_values = {
      'user': user,
      'work': work,
      'book': book,
      'chapter': chapter,
      'verses': verses
    }
    path = os.path.join(os.path.dirname(__file__), 'chapter.html')
    self.response.out.write(template.render(path, template_values))


class SearchHandler(webapp.RequestHandler):

  def post(self):
    text = self.request.get('text')
    verses = Verse.all().search(text)
    template_values = {
      'verses': verses
    }
    path = os.path.join(os.path.dirname(__file__), 'search.html')
    self.response.out.write(template.render(path, template_values))


class NewBookmarkHandler(webapp.RequestHandler):

  def get(self):
    books = Book.all()
    book = None
    chapter = None
    book_id = self.request.get('book')
    chapter_number = self.request.get('chapter')
    if book_id:
      book = Book.gql('WHERE osis_id = :1', book_id).get()
    if book and chapter_number:
      chapter = book.chapters[int(chapter_number) - 1]
    bookdata = {}
    for b in books:
      chapterdata = { 'chapterCount': b.get_chapter_count() }
      for c in b.chapters:
        chapterdata[c.number] = c.get_verse_count()
      bookdata[b.osis_id] = chapterdata
    #logging.info(bookdata)
    template_values = {
      'books': books,
      'book': book,
      'chapter': chapter,
      'bookdata': simplejson.dumps(bookdata)
    }
    path = os.path.join(os.path.dirname(__file__), 'new_bookmark.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    user = users.get_current_user()
    book = Book.gql('WHERE osis_id = :1', self.request.get('book')).get()
    chapter = book.chapters.filter('number =', long(self.request.get('chapter'))).get()
    verse = chapter.verses.filter('number =', long(self.request.get('verse'))).get()
    comments = self.request.get('comments')

    bookmark = Bookmark(user=user, chapter=chapter, verse=verse, comments=comments)
    bookmark.save()

    self.redirect('/bookmark/')


class BookmarkHandler(webapp.RequestHandler):

  def get(self, bookmark_key):
    if bookmark_key:
      bookmark = Bookmark.get(bookmark_key)
      template_values = {
        'bookmark': bookmark
      }
      path = os.path.join(os.path.dirname(__file__), 'bookmark.html')
    else:
      user = users.get_current_user()
      bookmarks = Bookmark.gql('WHERE user = :1', user).fetch(20) # TODO: page bookmarks
      template_values = {
        'bookmarks': bookmarks
      }
      path = os.path.join(os.path.dirname(__file__), 'bookmark_list.html')

    self.response.out.write(template.render(path, template_values))

  def post(self):
    # TODO
    self.redirect('/bookmarks')


def main():
  application = webapp.WSGIApplication([('/', MainHandler),
                                        (r'/book/([^/]+)/([^/]+)/(\d+)/(\d+)', ChapterHandler),
                                        (r'/book/([^/]+)/([^/]+)/(\d+)', ChapterHandler),
                                        (r'/book/([^/]+)/([^/]+)', BookHandler),
                                        ('/search', SearchHandler),
                                        ('/bookmark', NewBookmarkHandler),
                                        (r'/bookmark/(.*)', BookmarkHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
