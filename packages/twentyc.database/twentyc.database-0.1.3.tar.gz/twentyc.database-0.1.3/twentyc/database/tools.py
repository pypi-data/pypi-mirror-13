import twentyc.database
import os
import re

def update_views(couch_engine, config, path):

  if couch_engine == "couchbase":
    raise Exception("Couchbase is currently not supported by this script.")

  t = re.sub("\.ddoc$", "", os.path.basename(path)).split("-")

  if len(t) != 2:
    return

  target = t[0]
  design_name = t[1]

  if not config.get("db_%s" % target):
    print "Skipping %s because '%s' is an unknown target" % (path, target)
    return

  client = twentyc.database.ClientFromConfig(couch_engine, config, target)

  view_f = open(path, "r")
  view_d = view_f.read().replace("\n"," ")
  view_f.close()


  print "Updating design from '%s' to '%s:%s/_design/%s'" % (
    path,
    couch_engine,
    client.database_name,
    design_name
  )

  client.put_design(
    design_name, view_d, verbose=True
  )


