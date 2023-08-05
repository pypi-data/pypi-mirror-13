"""
20c databse tools - allows for quick creation of db client instances based on engine (couchdb, couchbase ...)
"""

class InvalidEngineException(Exception):
  pass

def Client(engine="couchbase", host="", auth="", database="", logger=None, verbose=True):
  
  """
  Return new database client

  Arguments

  engine <str> defines which engine to use, currently supports "couchdb" and "couchbase"
  host <str|couchdb.Server> host url, when using couchdb this can also be a server instance
  auth <str> bucket_auth for couchbase, auth for couchdb
  database <str> database name for couchdb
  logger <Logger> python logger instance
  """

  if engine == "couchbase":
    from twentyc.database.couchbase.client import CouchbaseClient
    return CouchbaseClient(
      host, bucket_auth=auth, logger=logger
    )
  elif engine == "couchdb":
    from twentyc.database.couchdb.client import CouchDBClient
    return CouchDBClient(
      host, database, auth=auth, logger=logger, verbose=verbose
    )
  elif engine == "dummydb":
    from twentyc.database.dummydb.client import DummyDBClient
    return DummyDBClient()
  else:
    raise InvalidEngineException(engine)


def ClientFromConfig(engine, config, database, logger=None, verbose=True):
  """
  Return new database client from valid [couchdb] or [couchbase]
  config section.

  engine <str> defines which engine to use, currently supports "couchdb" and "couchbase"
  config <dict> [couchdb] or [couchbase] section from config
  database <str> token to use with bucket_%s or db_%s config property
  """

  if type(config) == list:
    config = dict(config)

  if engine == "couchbase":
    return Client(
      engine=engine,
      host=config.get("host"),
      auth=config.get("bucket_%s" % database),
      logger=logger,
      verbose=verbose
    )
  elif engine == "couchdb":
   
    if config.get("admin_user") and config.get("admin_password"):
      auth = "%s:%s" % (config.get("admin_user"), config.get("admin_password"))
    elif config.get("user") and config.get("password"):
      auth = "%s:%s" % (config.get("user"), config.get("password"))
    else:
      auth = None

    return Client(
      engine=engine,
      host=config.get("host"),
      auth=auth,
      database=config.get("db_%s" % database),
      logger=logger,
      verbose=verbose
    )
  elif engine == "dummydb":
    return Client(
      engine=engine
    )
  else:
    raise InvalidEngineException(engine)

def import_data(source, target):
  """
  Import all data from one database engine to another

  Arguments

  source <Mixed> a twentyc database client
  target <Mixed> a twentyc database client
  """
  return
