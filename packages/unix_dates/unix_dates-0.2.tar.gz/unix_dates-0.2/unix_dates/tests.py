import unittest
import datetime
from unix_dates import UnixDate, UnixTimeDelta


class TestUnixDate(unittest.TestCase):
    def test_date(self):
        now = datetime.datetime.now()
        unix_time = UnixDate.to_unix_time(now)

        back_datetime = UnixDate.to_datetime(unix_time)
        self.assertEqual(back_datetime.year, now.year)
        self.assertEqual(back_datetime.month, now.month)
        self.assertEqual(back_datetime.day, now.day)
        self.assertEqual(back_datetime.hour, now.hour)
        self.assertEqual(back_datetime.minute, now.minute)
        self.assertEqual(back_datetime.second, now.second)

        back_unix_time = UnixDate.to_unix_time(back_datetime)
        self.assertEqual(back_unix_time, unix_time)
        self.assertEqual(UnixDate.to_datetime(back_unix_time), back_datetime)

    def test_parsing(self):
        d = UnixDate.to_unix_time_from_iso_format("2008-09-03T20:56:35.450686Z")
        dt = UnixDate.to_naive_datetime(d)

        self.assertEqual(dt.year, 2008)
        self.assertEqual(dt.month, 9)
        self.assertEqual(dt.day, 3)
        self.assertEqual(dt.hour, 20)
        self.assertEqual(dt.minute, 56)
        self.assertEqual(dt.second, 35)

        d = UnixDate.to_unix_time_from_aws_format("2015-12-24T16:46:19.166+0000")
        dt = UnixDate.to_naive_datetime(d)

        self.assertEqual(dt.year, 2015)
        self.assertEqual(dt.month, 12)
        self.assertEqual(dt.day, 24)
        self.assertEqual(dt.hour, 16)
        self.assertEqual(dt.minute, 46)
        self.assertEqual(dt.second, 19)

    def test_delta(self):
        self.assertEqual(UnixTimeDelta.calc(millis=1000), 1)
        self.assertEqual(UnixTimeDelta.calc(seconds=1), 1)
        self.assertEqual(UnixTimeDelta.calc(minutes=1), 60)
        self.assertEqual(UnixTimeDelta.calc(hours=1), 3600)
        self.assertEqual(UnixTimeDelta.calc(days=1), 3600 * 24)
