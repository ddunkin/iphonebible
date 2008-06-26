#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.ext import search

class Work(db.Model):
  osis_id = db.StringProperty()
  title = db.StringProperty()

class Book(db.Model):
  osis_id = db.StringProperty()
  work = db.ReferenceProperty(Work, collection_name='books')
  title = db.StringProperty()
  chapter_count = db.IntegerProperty()
  
  def get_chapter_count(self):
    """
    Gets the cached chapter count, or counts the chapters and saves the object
    with the cached value.
    """
    if self.chapter_count == None:
      self.chapter_count = self.chapters.count()
      self.put()
    return self.chapter_count

class Chapter(db.Model):
  osis_id = db.StringProperty()
  book = db.ReferenceProperty(Book, collection_name='chapters')
  number = db.IntegerProperty()
  title = db.StringProperty()
  verse_count = db.IntegerProperty()
  
  def get_verse_count(self):
    """
    Gets the cached verse count, or counts the verses and saves the object
    with the cached value.
    """
    if self.verse_count == None:
      self.verse_count = self.verses.count()
      self.put()
    return self.verse_count

class Verse(search.SearchableModel):
  osis_id = db.StringProperty()
  chapter = db.ReferenceProperty(Chapter, collection_name='verses')
  number = db.IntegerProperty()
  text = db.TextProperty()
  _bookmark = None

  def address(self):
    return "%s %d:%d" % (self.chapter.book.title, self.chapter.number, self.number)

  def get_bookmark(self):
    return self._bookmark

class Bookmark(db.Model):
  # denormalize chapter from verse for efficiency when searching
  #  for bookmarks in a chapter
  chapter = db.ReferenceProperty(Chapter, collection_name='bookmarks')
  verse = db.ReferenceProperty(Verse, collection_name='bookmarks')
  user = db.UserProperty()
  comments = db.TextProperty()

  def address(self):
    return self.verse.address()

