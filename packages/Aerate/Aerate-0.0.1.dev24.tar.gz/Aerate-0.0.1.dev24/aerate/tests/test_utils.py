from aerate.tests import TestBase
from aerate.utils import str_to_date
import datetime


class TestUtils(TestBase):

    def setUp(self):
        super(TestUtils, self).setUp()

    def test_str_to_date_returns_string(self):
        datestring = 'Thu, 21 Jan 2016 21:15:56 GMT'
        time = str_to_date(datestring)
        self.assertTrue(isinstance(time, datetime.datetime))
