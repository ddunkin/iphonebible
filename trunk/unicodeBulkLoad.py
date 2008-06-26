#!/usr/bin/env python

import StringIO
import csv
import httplib
import sys
import traceback

from unicodeCsv import UnicodeReader

import wsgiref.handlers

from google.appengine.ext import bulkload
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.ext import search
from google.appengine.ext import webapp

class UnicodeBulkLoad(bulkload.BulkLoad):
  def Load(self, kind, data):
    """ Parses CSV data, uses a Loader to convert to entities, and stores them.

    On error, fails fast. Returns a "bad request" HTTP response code and
    includes the traceback in the output.

    Args:
      kind: a string containing the entity kind that this loader handles
      data: a string containing the CSV data to load

    Returns:
      tuple (response code, output) where:
        response code: integer HTTP response code to return
        output: string containing the HTTP response body
    """
    bulkload.Validate(kind, basestring)
    bulkload.Validate(data, basestring)
    output = []

    try:
      loader = bulkload.Loader.RegisteredLoaders()[kind]
    except KeyError:
      output.append('Error: no Loader defined for kind %s.' % kind)
      return (httplib.BAD_REQUEST, ''.join(output))

    buffer = StringIO.StringIO(data)
    reader = UnicodeReader(buffer, skipinitialspace=True)

    try:
      csv.field_size_limit(800000)
    except AttributeError:
      pass

    entities = []

    line_num = 1
    for columns in reader:
      if columns:
        try:
          output.append('\nLoading from line %d...' % line_num)
          new_entities = loader.CreateEntity(columns)
          if new_entities:
            entities.extend(new_entities)
          output.append('done.')
        except:
          exc_info = sys.exc_info()
          stacktrace = traceback.format_exception(*exc_info)
          output.append('error:\n%s' % stacktrace)
          return (httplib.BAD_REQUEST, ''.join(output))

      line_num += 1

    for entity in entities:
      datastore.Put(entity)

    return (httplib.OK, ''.join(output))

