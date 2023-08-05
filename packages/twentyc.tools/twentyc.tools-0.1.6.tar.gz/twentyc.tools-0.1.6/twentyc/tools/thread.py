from threading import Thread

###############################################################################
# Classes
###############################################################################

class RunInThread(Thread):
  
  """
  Extends threading.Thread
  
  Example:

  t = RunInThread(my_func)
  t.start("some text")
  will call my_func("some text") in it's own thread
  """

  error_handler = None
  
  def __init__(self, callback):
    
    """
    Init and set callback function, the callback function
    will be executed on run()
    """
    
    Thread.__init__(self)
    self.callback = callback
    self.result_handler = None

  def run(self):
    try:
      r = self.callback(*self.runArgs, **self.runKwargs)
      if self.result_handler:
        self.result_handler(r)
    except Exception, inst:
      if self.error_handler:
        self.error_handler(inst)
      else:
        raise
    del self.callback
    del self.runArgs
    del self.runKwargs

  def start(self, *args, **kwargs):
    
    """
    Set the arguments for the callback function and start the
    thread
    """

    self.runArgs = args
    self.runKwargs = kwargs
    Thread.start(self)


