"""
`tid` is the Swedish word for time.
"""
from datetime import datetime, timedelta
import calendar
from .utils import cached_property


# ISO 8601 http://www.w3.org/TR/NOTE-datetime
ISO_8601 = '%Y-%m-%dT%H:%M:%S.%fZ'
RFC_3339 = '%Y-%m-%dT%H:%M:%SZ'


class DateTime(datetime):

    @cached_property
    def seconds_from_epoch(self):
        """
            Returns seconds since epoch (1970, 1, 1, 0, 0, 0.0) in utc time
            [float]
            N.B. includes microseconds
        """
        return calendar.timegm(
            self.utctimetuple()
        ) + self.microsecond * 10.**-6

    @cached_property
    def iso8601(self):
        return self.strftime(ISO_8601)

    @cached_property
    def rfc3339(self):
        return self.strftime(RFC_3339)

    def past_timestamp(self, template=None, **kwargs):
        dtime = self - timedelta(**kwargs)
        return dtime.timestamp(template=template)

    def timestamp(self, template=None):
        """
            Return a string in the time template specified
        """
        if template is None:
            return self.seconds_from_epoch
        return self.strftime(template)

    @classmethod
    def convert(cls, instance):
        return cls(
            instance.year,
            instance.month,
            instance.day,
            instance.hour,
            instance.minute,
            instance.second,
            instance.microsecond,
            instance.tzinfo
        )

    def __add__(self, other):
        result = super(DateTime, self).__add__(other)
        return DateTime.convert(result)

    def __sub__(self, other):
        result = super(DateTime, self).__sub__(other)
        return DateTime.convert(result)

    __radd__ = __add__
    __rsub__ = __sub__
