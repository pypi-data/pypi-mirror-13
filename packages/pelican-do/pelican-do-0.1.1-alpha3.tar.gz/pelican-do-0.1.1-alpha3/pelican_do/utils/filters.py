
# Custom filter method
def rst_title(s):
  return s + '\n' + '#' * len(s) + '\n'

def pelican_datetime(value):
  return value.strftime('%Y-%m-%d %H:%M')



