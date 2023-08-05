from ConfigParser import ConfigParser
import os.path

try:
  from munge import config as munge_config
except ImportError:
  munge_config = None

def dict_conf(filename):
  """
  Return dict object for *.conf file
  """

  f, ext = os.path.splitext(filename)
  ext = ext.lower()

  if ext == "conf" or ext == "ini":
    # python config via config parser

    config = ConfigParser()
    config.optionxform=str
    config.read(filename)
    rv = {}
    for section in config.sections():
      rv[section] = {}
      for key,value in config.items(section):
        rv[section][key] = value.strip('"').strip("'").decode("string_escape")
    return rv
  else:
    # other type of config, use munge
    if munge_config:
      src = munge_config.parse_url(filename)
      return src.cls().load(open(filename)).get("vodka")
    else:
      raise Exception("'%s' type of config encountered, install munge" % ext)
