"""
CouchDB client abstraction with automatic json encoding and decoding
"""

import couchdb
import simplejson as json
import re
import time
import threading
import requests

class RESTException(Exception):
  pass

def cleanup(rv):
  lst = [':','_']
  for k,v in rv.items():
    if k[0] in lst:
      del rv[k]
  return rv

class CouchDBClient(object):

  # arguments parsed from the provided url
  host = ""
  bucket_name = ""
  password = ""

  # couchdb client
  cb = None

  # bucket object
  bucket = None

  # logger instance
  log = None

  meta_prefix = ":"

  def __init__(self, host, database, auth="", logger=None, autocreate=True, verbose=True):
    """
    Init and connect to a couchdb database.

    Args

    host <string|couchdb.Server> hostname (can include port separated by :) - it is also valid
      to pass an existing couchdb.Server instance here.

    database <string> name of database to use

    Keyword arguments

    auth <string> database auth if any - "user:password" expected
    logger <logger> python logger instance to log debug and info messages
    autocreate <bool> if true automatically create the database specified in 'datatbase' if
      it does not exist.
    verbose <bool> if true dbg message will be printed
    """

    try:

      self.verbose = verbose

      user = None
      password = None
      self.auth = None

      if type(host) in [str, unicode]:
        # parse and store url information
        if auth:
          auth = auth.split(":")
          user = auth[0]
          if len(auth) > 1:
            password = auth[1]
            self.auth = tuple(auth)

        if not re.search("^http", host):
          host = "http://%s" % host

      # attempt to connect to database
      self.server = self.cb = couchdb.Server(host)
      self.host = self.cb.resource.url;
      self.database_name = database;
      self.logger = logger


      if user and password:
        self.cb.resource.credentials = (user, password)

      try:
        self.db = self.bucket = self.cb[database]
      except couchdb.ResourceNotFound, inst:
        if autocreate:
          self.db = self.bucket = self.cb.create(database)
        else:
          raise

      self.log = logger
      self.dbg("Initialized")
    except:
      raise


  #############################################################################

  def dbg(self, msg):

    str = "CouchDB(%s/%s): %s" % (self.host, self.database_name, msg)
    if self.log:
      self.log.debug(str)
    if self.verbose:
      print str

  #############################################################################

  def unset(self, key):
    """
    Delete object indexed by <key>
    """

    try:
      try:
        self.bucket.delete(self.get(key))
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
      except:
        raise

      return dict(obj or {})

    except:
      raise

  #############################################################################

  def set(self, key, data, retry=0):

    """
    Store data <data> index by key <key>

    Args

    key <string> couchdb document id
    data <dict> data to store
    """

    try:

      if type(data) != dict:
        raise Exception("data needs to be of type <dict>")

      #t1 = time.time()

      if not data.has_key("_rev"):
        exists = self.bucket.get(key)
        if exists:
          data["_rev"] = exists.get("_rev")
      data["_id"] = key
      try:
        #print "Preparing save: %s %s" % (key, data)
        (id, rev) = self.bucket.save(data)
      except couchdb.http.ResourceConflict, inst:
        if retry > 0:
          if data.has_key("_rev"):
            del data["_rev"]
          retry -= 1
          return self.set(key, data, retry=retry)
        else:
          if self.logger:
            self.logger.error("Document update conflict '%s' on '%s', rev '%s'" % (inst, key, data.get("_rev")))
            return 0
          else:
            raise

      return rev

      #print "Saved in %.5f" % (time.time() - t1)
    except:
      raise

  #############################################################################

  def set_batch(self, data):
    
    """
    Store multiple documents
    
    Args

    data <dict> data to store, use document ids as keys

    Returns

    revs <dict> dictionary of new revisions indexed by document ids
    """

    # fetch existing documents to get current revisions
    rows = self.bucket.view("_all_docs", keys=data.keys(), include_docs=True)
    existing = {}
    for row in rows:
      key = row.id
      if key and not data[key].has_key("_rev"):
        data[key]["_rev"] = row.doc["_rev"]

    for id,item in data.items():
      data[id]["_id"] = id

    revs = {}
    for success, docid, rev_or_exc in self.bucket.update(data.values()):
      if not success and self.logger:
        self.logger.error("Document update conflict (batch) '%s', %s" % (docid, rev_or_exc))
      elif success:
        revs[docid] = rev_or_exc

    return revs



  #############################################################################

  def view(self, design_name, view_name, **kwargs):
    try:

      # convert boolean stale argument to something couchdb understands
      if kwargs.get("stale") == False:
        del kwargs["stale"]
      elif kwargs.get("stale") == True:
        kwargs["stale"] = "ok"

      v = self.bucket.view("%s/%s" % (design_name, view_name), **kwargs)
      return v

    except:
      raise

  #############################################################################

  def xview(self, design_name, view_name, buffer=2000, **kwargs):
    return self.bucket.iterview("%s/%s" % (design_name, view_name), buffer, **kwargs)


  #############################################################################

  def regenerate_view(self, design_name, view_name):
    #self.dbg("Triggering view regen for %s %s" % (design_name, view_name))
    v = self.view(design_name, view_name, limit=1)
    # need to do this to actually trigger the regen part
    for row in v:
      continue

  #############################################################################

  def regenerate_all_views(self, design_name):
    design = self.get_design(design_name)
    for name, view in design.get("views", {}).items():
      self.regenerate_view(design_name, name)

  #############################################################################

  def regenerate_all_views_forever(self, design_names, interval):

    db = self
    def regen():
      while True:
        for name in design_names:
          db.regenerate_all_views(name)
        time.sleep(interval)

    t = threading.Thread(target=regen)
    t.daemon = True
    t.start()

    return t

  #############################################################################

  def recent_docs(self, include_docs=True, limit=None):

    """
    Retrieve recently changed / added docs


    Args:

    include_docs <bools> if true full document data will be retrieved
    limit <int> if != None and > 0 limit the result set to this amount of rows

    Returns a view result to be iterated through
    """

    try:
      return self.bucket.view("_changed", include_docs=include_docs, limit=limit)
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

  #############################################################################

  def get_design(self, design_name):
    """
    Returns dict representation of the design document with the matching
    name

    design_name <str> name of the design
    """

    try:
      r = requests.request(
        "GET",
        "%s/%s/_design/%s" % (
          self.host,
          self.database_name,
          design_name
        ),
        auth=self.auth
      )

      return self.result(r.text)

    except:
      raise

  #############################################################################

  def del_design(self, design_name):
    """
    Removes the specified design

    design_name <str>
    """

    try:

      design = self.get_design(design_name)
      r = requests.request(
        "DELETE",
        "%s/%s/_design/%s" % (
          self.host,
          self.database_name,
          design_name
        ),
        params={"rev" : design.get("_rev")},
        auth=self.auth
      )
      return self.result(r.text)

    except:
      raise

  #############################################################################

  def put_design(self, design_name, design, verbose=False):
    """
    Updates a design document for the loaded databases

    design_name <str> name of the design
    design <str> json string of the design document
    """

    try:

      try:
        # check if there is a previous revision of the
        # specified design, if there is get the _rev
        # id from it and apply it to the new version
        existing = self.get_design(design_name)

        design = json.loads(design)

        if design.get("version") and existing.get("version") == design.get("version"):
          if verbose:
            print "No change in design... skipping update!"
          return

        design["_rev"] = existing["_rev"]
        design = json.dumps(design)
      except RESTException:
        pass

      r = requests.request(
        "PUT",
        "%s/%s/_design/%s" % (
          self.host,
          self.database_name,
          design_name
        ),
        auth=self.auth,
        data=design,
        headers={"content-type" : "application/json"}
      )

      return self.result(r.text)

    except:
      raise

  #############################################################################


  def result(self, couchdb_response_text):
    """
    Return whether a REST couchdb operation was successful or not.

    On error will raise a RESTException
    """
    result = json.loads(couchdb_response_text)

    if result.get("ok"):
      return True
    elif result.get("error"):
      raise RESTException(
        "%s: %s" % (result.get("error"), result.get("reason"))
      )
    return result



