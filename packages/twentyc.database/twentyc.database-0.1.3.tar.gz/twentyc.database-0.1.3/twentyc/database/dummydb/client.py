"""
Dummy DB client that sends to void and returns empty dicts
"""


class DummyDBClient(object):

  meta_prefix = ":"
  log = None
  cb = None
  bucket = None
  
  def __init__(self, *args, **kwargs):
    return

  #############################################################################

  def unset(self, key):
    return

  #############################################################################

  def get(self, key):
    return {}

  #############################################################################

  def set(self, key, data, retry=0):
    return 1

  #############################################################################

  def set_batch(self, data):
    return {} 

  #############################################################################

  def view(self, design_name, view_name, **kwargs):
    return []

  #############################################################################

  def xview(self, design_name, view_name, buffer=2000, **kwargs):
    return []

  #############################################################################

  def regenerate_view(self, design_name, view_name):
    return

  #############################################################################

  def regenerate_all_views(self, design_name):
    return

  #############################################################################

  def regenerate_all_views_forever(self, design_names, interval):
    return 

  #############################################################################

  def recent_docs(self, include_docs=True, limit=None):
    return []

  #############################################################################

  def dump(self, key):
    return "{}"


  #############################################################################

  def get_design(self, design_name):
    return {}

  #############################################################################

  def del_design(self, design_name):
    return

  #############################################################################

  def put_design(self, design_name, design, verbose=False):
    return

  #############################################################################

  def result(self, couchdb_response_text):
    return True
