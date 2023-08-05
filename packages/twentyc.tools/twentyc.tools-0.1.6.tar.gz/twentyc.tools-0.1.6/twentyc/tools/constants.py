ACCESS_READ = 0x01
ACCESS_WRITE = 0x02
ACCESS_XBAHN_WRITE = 0x04

def access_xl(level):
  a = ''
  if level & ACCESS_READ:
    a = 'R'
  if level & ACCESS_WRITE:
    a += 'W'
  if level & ACCESS_XBAHN_WRITE:
    a += 'X'

  if not a:
    a = 'D'

  return a

