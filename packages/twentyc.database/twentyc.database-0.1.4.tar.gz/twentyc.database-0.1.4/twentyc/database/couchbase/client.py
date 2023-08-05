"""
Couchbase client abstraction with automatic json encoding and decoding
"""

from urlparse import urlparse
from couchbase.client import Couchbase
import couchbase.exception
import json

class CouchbaseClient(object):

  # arguments parsed from the provided url
  host = ""
  bucket_name = ""
  password = ""

  # couchbase client
  cb = None

  # bucket object
  bucket = None

  # logger instance
  log = None

  meta_prefix = ":"

  def __init__(self, host, bucket_auth="default", logger=None):
    """
    Init and connect to a couchbase database.

    Args

    host <string> hostname (can include port separated by :)

    Keyword arguments
    
    bucket_auth <string> bucket to load with possibility of also providing a password delimited 
    by ":" - defaults to "default"
    logger <logger> python logger instance to log debug and info messages
    """

    try:

      # parse and store url information
      bucket_auth = bucket_auth.split(":")
      self.host = host 
      self.bucket_name = bucket_auth[0]
      if len(bucket_auth) > 1:
        self.password = bucket_auth[1]
      self.log = logger

      # attempt to connect to database
      self.cb = Couchbase(self.host, self.bucket_name, self.password)

      # get bucket
      self.dbg("Setting bucket: %s" % self.bucket_name)
      self.bucket = self.cb.bucket(self.bucket_name)


    except:
      raise


  #############################################################################

  def dbg(self, msg):
    
    str = "Couchbase(%s/%s): %s" % (self.host, self.bucket_name, msg)
    if self.log:
      self.log.debug(str)
      print str
    else:
      print str

  #############################################################################

  def unset(self, key):
    """
    Delete object indexed by <key>
    """

    try:
      try:
        self.bucket.delete(key)
      except couchbase.exception.MemcachedError, inst: 
        if str(inst) == "Memcached error #1:  Not found":
          # for some reason the py cb client raises an error when
          # a key isnt found, instead we just want a none value.
          return
        else:
          raise
      except:
        raise
    except:
      raise


  #############################################################################

  def get(self, key):
    
    """
    Retrieve object indexed by <key>
    """

    try:
      try:
        obj = self.bucket.get(key)
      except couchbase.exception.MemcachedError, inst: 
        if str(inst) == "Memcached error #1:  Not found":
          # for some reason the py cb client raises an error when
          # a key isnt found, instead we just want a none value.
          obj = None
        else:
          raise
      except:
        raise
      
      if obj:
        return json.loads(obj[2])
      else:
        return None

    except:
      raise

  #############################################################################

  def set(self, key, data, retry=0):
    
    """
    Store data <data> index by key <key>

    Args

    key <string> couchbase document id
    data <dict> data to store
    """
    
    try:

      if type(data) != dict:
        raise Exception("data needs to be of type <dict>")

      self.bucket.set(key, 0, 0, json.dumps(data))

    except:
      raise

  #############################################################################

  def view(self, design_name, view_name, **kwargs):
    try:
      
      v = self.bucket.view("_design/%s/_view/%s" % (design_name, view_name), **kwargs)
      return v

    except:
      raise

  #############################################################################

  def dump(self, key):
    
    """
    Retrieve object indexed by <key> and return it serialized
    """

    try:
      
      obj = self.get(key)
      if obj:
        return json.dumps(obj)
      else:
        return None

    except:
      raise


#client = Couchbase("127.0.0.1:8091", "default", "");

#client.create("vegutest", "test123")

#    def create(self, bucket_name, bucket_password='', ram_quota_mb=100,
#                   replica=0):

#bucket = client.bucket("default")

#testobj = {
#  "hello" : "world"
#}

#bucket.set("hello-world", 0, 0, json.dumps(testobj))

#testobj = json.loads(bucket.get("hello-world")[2])

#print str(testobj)
