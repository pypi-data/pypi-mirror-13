import subprocess
import cmd
import os
import shutil
import subprocess
import commands
import re
import optparse
import ConfigParser
import signal
import time

from twentyc.tools.config import dict_conf

DEBUG = False

class ConfigNotFound(Exception):
  def __init__(self, fileName):
    Exception.__init__(self, "Config not found: %s" % fileName)

###############################################################################

class ConfigValueInvalid(Exception):
  def __init__(self, section, key, expecting):
    Exception.__init__(self, "Invalid value for %s:%s -> expecting %s" % (section,
      key, expecting))

class ConfigValueMissing(Exception):
  def __init__(self, section, key):
    Exception.__init__(self, "Missing value for %s:%s" % (section, key)) 

class InvalidCommand(Exception):
  def __init__(self, name):
    Exception.__init__(self, "Invalid command: %s" % name)

################################################################################

class CLIEnv(cmd.Cmd):

  def __init__(self, name="cli"):
    cmd.Cmd.__init__(self)
    self.serving = False
    self.name = name
    self.xbahn = {}
    self.optparse = optparse.OptionParser()
    self.custom_options()
    self.config_errors = []

  #############################################################################

  def custom_options(self):
    self.optparse.add_option("-c", "--config", dest="configfile", default="%s.conf" % self.name, help="path to cli config file, defaults to ./%s.conf" % self.name)
    
  #############################################################################

  def check_config(self, section, name, has_default=False, value=None, allowEmpty=False):
    
    """
    Check if a config value is set

    Returns

    True - config value is set and valid
    False - config value is not set or invalid
    """

    cfg = self.config
    if not cfg.has_key(section) or not cfg.get(section).has_key(name):
      if not has_default:
        self.config_errors.append("%s: %s -> missing" % (section, name))
        return False
      else:
        return True

    v = cfg.get(section).get(name)

    if v == "" and not allowEmpty:
      self.config_errors.append("%s: %s -> empty" % (section, name))
      return False
    return True

  #############################################################################


  def require_config(self, section, name, has_default=False, value=None, allowEmpty=False):
    cfg = self.config
    if not cfg.has_key(section) or not cfg.get(section).has_key(name):
      if not has_default:
        raise ConfigValueMissing(section, name)
      else:
        return value

    v = cfg.get(section).get(name)

    if v == "" and not allowEmpty:
      raise ConfigValueMissing(section, name)
    return v

  def need_config_file(self):
    return True

  def run(self):

    # parse options
    (options, args) = self.optparse.parse_args()
    self.options = options
    self.args = args

    if len(args) > 0:
      self.run_command = args[0]
    else:
      self.run_command = None

    # load config
    self.configfile = os.path.expandvars(options.configfile)
    
    if self.need_config_file():
      if not os.path.exists(self.configfile):
        raise ConfigNotFound(self.configfile)

    if os.path.exists(self.configfile):
      print "Using config: %s" % self.configfile
      self.config = dict_conf(self.configfile) 
    else:
      self.config = {}

    # shutdown cleanly
    signal.signal(signal.SIGINT, self.shutdown)
    signal.signal(signal.SIGTERM, self.shutdown)

  def connect_xbahn(self):
    import twentyc.xbahn.pool as xbahn_pool
    xbahn_pool.connect_from_config(self.config, start=True)
    self.xbahn = xbahn_pool.instances

  def xbahn_request_to_all(self, namespace, data, **kwargs):
    import twentyc.xbahn.pool as xbahn_pool
    return xbahn_pool.request_to_all(namespace, data, **kwargs)

  def xbahn_find_instance(self, conn_str):
    import twentyc.xbahn.pool as xbahn_pool
    return xbahn_pool.find(conn_str)

  def print_table(self, headers, data):
    try:
      import prettytable
    except Exception, inst:
      print "PrettyTable python module not installed, but is required for this operation"
      return
    print "Printing table with headers: %s" % headers
    table = prettytable.PrettyTable(headers)
    for row in data:
      table.add_row([row.get(k) for k in headers])
    print table

  def serve(self):
    self.serving = True
    while(self.serving):
      self.work()
      time.sleep(1)

  def works(self):
    pass

  def shutdown(self, *args):
    print "Shutting down..."
    self.serving = False
    if self.xbahn:
      import twentyc.xbahn.pool as xbahn_pool
      xbahn_pool.disconnect()

  def require_env_var(self, name, default):
    if not os.environ.has_key(name):
      self.set_env_var(name, default)

  def set_env_var(self, name, value):
    os.environ[name] = str(value)
    print "export %s=%s" % (name, value)

  def copyfiles(self, src, dst, symlinks=False):
    if DEBUG:
      print "Copying files from '%s' to '%s'" % (src, dst)

    if not os.path.exists(dst):
      os.makedirs(dst)

    if not os.path.isdir(src):
      shutil.copy(src, dst)
      return

    for item in os.listdir(src):
      s = os.path.join(src, item)
      d = os.path.join(dst, item)
      if os.path.isdir(s):
        shutil.copytree(s, d, symlinks=symlinks)
      else:
        shutil.copy2(s, d)
  
  def run_shell(self, cmd):
    if DEBUG:
      print "Executing: %s" % cmd
    subprocess.check_call(cmd.split(' '))

  def warn(self, msg):
    print "WARNING: %s"% msg

  def notify(self, msg):
    print msg



################################################################################

def rm_rf(dir):
  if not os.path.exists(dir):
    return
  for root, dirs, files in os.walk(dir, topdown=False):
    for name in files:
      os.remove(os.path.join(root, name))
    for name in dirs:
      os.rmdir(os.path.join(root, name))
  os.rmdir(dir)


###############################################################################

class Command:
  def __init__(self, opt):
    self.options = opt
    self.min_prefix = ""
    self.min_keep_original = True

  def _exec(self, cmd):
    subprocess.check_call(cmd.split(' '))

  def _yuizip(self, src, dst):
    if self.options.nocompress:
      return

    rv, jar = commands.getstatusoutput("ls " + self.options.yuidir + "/build/yuicompressor-*.jar")

    if rv:
      raise RuntimeError("yuicompressor jar not found (" + self.options.yuidir + ")")

    cmd = "java -jar " + jar
    try :
      self._exec(cmd + " " + src + " -o " + dst)
    except OSError :
      print 'encountering OSError while calling java to run yuicompressor, you likely do not have java installed.'
      raise

  def _googlezip(self, src, dst):
    if self.options.nocompress:
      return

    rv, jar = commands.getstatusoutput("ls " + self.options.closurecompilerdir + "/compiler.jar")

    if rv:
      raise RuntimeError("compiler.jar not found (" + self.options.closurecompilerdir + ")")

    cmd = "java -jar " + jar
    try :
      self._exec(cmd + " --js " + src + " --js_output_file " + dst)
    except OSError :
      print 'encountering OSError while calling java to run closure compiler, you likely do not have java installed.'
      raise

  ##############################################################################

  def _install_dir(self, src, targ, DESTDIR):
    dst = DESTDIR + targ
    if not os.path.exists(dst):
      raise RuntimeError("Destination (" + dst + ") does not exist while installing " + src)

    for root, dirs, files in os.walk(src): #, topdown=False):
      if ".svn" in dirs:
        dirs.remove(".svn")
      if ".git" in dirs:
        dirs.remove(".git")

      dir = dst + "/" + root
      print "mkdir " + dir
      if not os.path.exists(dir):
        os.makedirs(dir)

      for name in dirs:
        dir = dst + "/" + root + "/" + name
        print "mkdir " + dir
        if not os.path.exists(dir):
          os.makedirs(dir)
        k = root+"/"+name
        if os.path.islink(k):  
          print "copying symlink dir %s" % k
          shutil.rmtree(dir)
          shutil.copytree(k, dir)

      for name in files:
        srcfile = root + "/" + name
        dstfile_min = dst + "/" + ("%s/%s%s" % (root, self.min_prefix, name))
        dstfile = dst + "/" + srcfile

        if re.match("^%s" %self.min_prefix, name):
          continue

        if name.endswith(".js") and not self.options.nocompress and not name in ["yui.js"]:
          if self.min_keep_original:
            shutil.copyfile(srcfile, dstfile)
          if not self.options.useclosurecompiler:
            self._yuizip(srcfile, dstfile_min)
          else:
            self._googlezip(srcfile, dstfile_min)
        elif name.endswith(".css") and not self.options.nocompress:
          self._yuizip(srcfile, dstfile_min)
        else:
          shutil.copyfile(srcfile, dstfile)
        print "  " + srcfile

  ##############################################################################

  def _install_file(self, src, targ, DESTDIR):
    pass


