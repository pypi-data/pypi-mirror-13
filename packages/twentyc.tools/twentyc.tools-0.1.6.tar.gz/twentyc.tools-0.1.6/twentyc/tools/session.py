import re 

#############################################################################

def perms_structure(perms):
  perms_wc = {}
  for ns, p in perms.items():
    pieces = ns.split(".")
    a = prev = perms_wc 
    n = 0 
    l = len(pieces)
    for k in pieces:
      if n < l-1:
        if not a.has_key(k):
          a[k] = {}
        elif type(a[k]) != dict:
          a["@%s"%k] = a[k]
          a[k] = {}
        a = a[k]
      else:
        if not a.has_key(k):
          a[k] = p
        else:
          a["@%s"%k] = p
      n += 1
   

  return perms_wc 

#############################################################################

def perms_check_fast(perms_structure,namespace):
  pieces = namespace.split(".")
  a = perms_structure
  for k in pieces:
    if not a.has_key(k) and not a.has_key("*"):
      return 0
    a = a.get(k, a.get("*"))
  return a

#############################################################################

def perms_check(perms, prefix, ambiguous=False):
  
  """
  Return the user's perms for the specified prefix

  perms <dict> permissions dict
  prefix <string> namespace to check for perms

  ambiguous <bool=False> if True reverse wildcard matching is active and a perm check for a.b.* will
  be matched by the user having perms to a.b.c or a.b.d - only use this if you know what 
  you are doing.
  """

  try:
   
    token = prefix.split(".")

    i = 1
    l = len(token)
    r = 0
    
    # collect permission rules with a wildcard in them, so we dont do unecessary
    # regex searches later on
    perms_wc = {}
    for ns, p in perms.items():
      if ns.find("*") > -1:
        perms_wc[re.escape(ns).replace("\*", "[^\.]+")] = p

    while i <= l:
      k = ".".join(token[:i])
      matched = False

      # check for exact match
      if perms.has_key(k):
        r = perms.get(k)

      # check for wildcard matches (if any wildcard rules exist)
      elif perms_wc:
        for ns, p in perms_wc.items():
          a = "^%s$" % ns
          b = "^%s\." % ns
          j = len(a)
          u = len(b)
          if j > matched and re.match(a, k):
            r = p
            matched = j
          elif u > matched and re.match(b, k):
            r = p
            matched = u
      
      # if not matched at all and ambiguous flag is true, do ambiguous matching
      if not matched and ambiguous:
        m = "^%s" % re.escape(k).replace("\*", "[^\.]+")
        for ns, p in perms.items():
          if re.match(m, ns) and p > r:
            r = p
            break

      i += 1

    return r
  except:
    raise



