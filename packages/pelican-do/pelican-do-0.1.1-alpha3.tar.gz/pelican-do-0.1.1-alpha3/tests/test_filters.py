import pytest

from pelican_do.utils.filters import rst_title, pelican_datetime

import re
import datetime
def test_rst_title():
  assert rst_title('This is a title') == 'This is a title\n###############\n'

def test_pelican_datetime():
  assert pelican_datetime(datetime.datetime(1982, 9, 1, 22, 11, 10)) == '1982-09-01 22:11'

