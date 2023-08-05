import datetime
import time


class UnixDate(object):
    iso_format_fmt = "%Y-%m-%dT%H:%M:%S"

    """
    Utilities to convert dates to Unix time and back.

    Unix timestamps are the format we use to store dates in the system. This is a consistent way to store dates - cross
    time-zones, efficiently, without having to parse strings back and forth.
    """

    class UTCTimeZoneInfo(datetime.tzinfo):

        UTC_OFFSET_SECONDS = -1 * (time.timezone if (time.localtime().tm_isdst == 0) else time.altzone)

        def utcoffset(self, dt):
            return datetime.timedelta(seconds=self.UTC_OFFSET_SECONDS)

        def dst(self, dt):
            return datetime.timedelta(0)

    UTC = UTCTimeZoneInfo()

    @classmethod
    def now(cls):
        """
        :rtype: float
        :return: The Unix epoch: number of seconds that have elapsed since January 1, 1970 (UTC)
        """
        return cls.to_unix_time(datetime.datetime.now())

    @classmethod
    def to_unix_time(cls, dt):
        """
        convert datetime to epoch
        :type dt: datetime.datetime
        :rtype: float
        :return: The Unix epoch: number of seconds that have elapsed since January 1, 1970
        """

        timetuple = dt.timetuple()
        return time.mktime(timetuple)

    @classmethod
    def to_unix_time_from_iso_format(cls, iso_format):
        """
        Old recording used that string isoformat in the create_time,
        :rtype: float
        :return: The Unix epoch: number of seconds that have elapsed since January 1, 1970
        """

        if isinstance(iso_format, (unicode, str,)):
            # is on 0 milliseconds
            # here are few solutions:
            #   http://stackoverflow.com/questions/30584364/python-strptime-format-with-optional-bits

            no_ms = iso_format.split('.')[0]
            value = datetime.datetime.strptime(no_ms, cls.iso_format_fmt)
            return cls.to_unix_time(value)

        else:
            raise ValueError("Failed convert {} {} to unix time".format(iso_format.__class__, iso_format))

    @classmethod
    def to_datetime(cls, unix_time_sec):
        """
        :type unix_time_sec: float
        :rtype: datetime.datetime
        """

        return datetime.datetime.fromtimestamp(timestamp=unix_time_sec, tz=cls.UTC)

    @classmethod
    def to_naive_datetime(cls, unix_time_sec):
        """
        :type unix_time_sec: float
        :rtype: datetime.datetime
        """

        return datetime.datetime.fromtimestamp(timestamp=unix_time_sec)


class UnixTimeDelta(object):
    """
    Convert time delta to unix time (allow easy calculations with UnixDate)
    """
    SECONDS_IN_HOUR = 60 * 60
    SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR

    @classmethod
    def calc(cls, days=0, hours=0, minutes=0, seconds=0, millis=0):
        return days * cls.SECONDS_IN_DAY + \
               hours * cls.SECONDS_IN_HOUR + \
               minutes * 60 + \
               seconds + \
               millis / 1000
