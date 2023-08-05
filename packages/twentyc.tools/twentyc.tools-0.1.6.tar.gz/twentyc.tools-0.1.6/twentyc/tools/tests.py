import optparse
import ConfigParser
import unittest2
import os
import json

try:
  import twentyc.xbahn.xbahn as xbahn
except ImportError, inst:
  print "No xbahn module available"
  xbahn = None

def line():
  return "\n--------------------------------------------------------------------------------"

def runtests(c, tests, extend_parser=None):
  parser = optparse.OptionParser()
  parser.add_option("-c", "--config", dest="configfile", default="$ZENFIRE_HOME/etc/$VODKA_CONFIG", help="path to a vodka config file with couchdb and xbahn information. Defaults to $ZENFIRE_HOME/etc/$VODKA_CONFIG")
  parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="print details")
  parser.add_option("-t", "--tests", dest="tests", default=None, help="can pass a comma separated list of tests to run only those tests")

  if extend_parser:
    extend_parser(parser)

  (options, args) = parser.parse_args()

  if options.tests:
    tests = options.tests.split(",")

  runner = unittest2.TextTestRunner(verbosity=2)
  suite = unittest2.TestSuite(map(c, tests))

  for test in suite:
    test.options = options

  result = runner.run(suite)
  return result

class TwentyCTestCase(unittest2.TestCase):

  def setUp(self, req_xbahn=False):

    self.configfile = os.path.expandvars(self.options.configfile)
    self.config = ConfigParser.RawConfigParser()
    self.config.read(self.configfile)

    self.verbose = self.options.verbose

    self.info("\nRead config from file: %s" % self.configfile)

    if self.config.has_section("server"):
      srvcnf = dict(self.config.items("server"))
      self.couch_engine = srvcnf.get("couch_engine", "couchdb")
      self.couch_config = dict(self.config.items(self.couch_engine))
    else:
      self.couch_engine = "none"
      self.couch_config = {}
    
    self.databases = {}

    if req_xbahn and self.config.has_section("xbahn"):
      self.xbahn_config = dict(self.config.items("xbahn"))
    elif req_xbahn:
      self.xbahn_config = {}

    if req_xbahn and xbahn:
      self.xbahn = xbahn.xBahnThread(
        self.xbahn_config.get("host"),
        int(self.xbahn_config.get("port",0)),
        self.xbahn_config.get("exchange"),
        None,
        None,
        queue_name="unittest2",
        username=self.xbahn_config.get("username"),
        password=self.xbahn_config.get("password"),
        verbose=self.verbose
      )
      self.xbahn.start()

  def tearDown(self):
    if hasattr(self, "xbahn") and self.xbahn.status == 2:
      self.info("Disconnecting xbahn!")
      self.xbahn.stop()
      self.xbahn.disconnect()

  def info(self, msg):
    if self.verbose:
      print msg

  def require(self, xbahn=False, databases=[]):
    if xbahn and (not hasattr(self, "xbahn") or self.xbahn.status!=2):
      raise self.skipTest("xbahn connection required")
    for db in databases:
      if db not in self.databases.keys():
        raise self.skipTest("database connection '%s'")

  def xbahn_client(self, queue_name):
    return xbahn.xBahnThread(
      self.xbahn_config.get("host"),
      int(self.xbahn_config.get("port")),
      self.xbahn_config.get("exchange"),
      None,
      None,
      queue_name=queue_name,
      username=self.xbahn_config.get("username"),
      password=self.xbahn_config.get("password"),
      verbose=self.verbose
    )
 

  def param_dump(self, param):
    if type(param) == dict:
      return json.dumps(param, indent=2)
    else:
      return "%s" % param

  def add_database(self, name, db):
    self.databases[name] = db

  def add_cli_options(self):
    pass

  def assertIsInstance(self, obj, cl, msg=None):
    self.assertTrue(type(obj) == cl, msg=msg)

  def assertIsIn(self, a, b, msg=None):
    self.assertTrue(a in b, msg=msg)

  def assertIsNotIn(self, a, b, msg=None):
    self.assertTrue(a not in b, msg=msg)
  
  def assertDictEqual(self, a, b ,msg=None, ignore=[]):
    
    msg = "dict mismatch: %s\nA:%s\nB:%s" % (
      msg,
      self.param_dump(a),
      self.param_dump(b)
    )

    for k in ignore:
      if a.has_key(k):
        del a[k]
      if b.has_key(k):
        del b[k]

    self.assertEqual(len(a.keys()), len(b.keys()), msg)
    for k,v in a.items():
      if k in ignore:
        continue

      if type(v) == dict:
        self.assertDictEqual(v, b.get(k), msg, ignore=ignore)
      elif type(v) == list:
        self.assertListEqual(v, b.get(k), msg)
      else:
        m = b.get(k)
        if m != v:
          raise Exception("values not equal: %s" % msg)
  
  def assertListEqual(self, a, b, msg=None):

    n = 0

    msg = "list mismatch: %s\nIS:%s\nSHOULD BE:%s" % (
      msg,
      a,
      b
    )

    self.assertTrue(len(a) == len(b), msg)
      
    for item_a in a:
      item_b = b[n]
      if type(item_a) == dict:
        self.assertDictEqual(item_a, item_b, msg)
      elif type(item_a) == list:
        self.assertListEqual(item_a, item_b, msg)
      else:
        self.assertEqual(item_a, item_b, msg)

      n += 1
    #self.assertTrue(set(a) == set(b), msg)

