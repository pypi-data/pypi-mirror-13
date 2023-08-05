from twisted.trial.unittest import TestCase
from datetime import datetime, timedelta

from ngen.tid import DateTime, ISO_8601, RFC_3339


class TimestampTests(TestCase):

    def setUp(self):
        self.now = DateTime.utcnow()
        self.epoch = DateTime(1970, 1, 1)


    def test_utcnow_instance(self):
        self.assertIsInstance(self.now, DateTime)

    def test_add(self):
        result = self.epoch + timedelta(days=1)
        self.assertIsInstance(result, DateTime)
        self.assertEqual(result.day, 2)

    def test_sub(self):
        result = self.epoch - timedelta(days=1)
        self.assertIsInstance(result, DateTime)
        self.assertEqual(result.day, 31)

    def test_radd(self):
        result = timedelta(days=1) + self.epoch
        self.assertIsInstance(result, DateTime)
        self.assertEqual(result.day, 2)

    def test_rsub(self):
        result = timedelta(days=1) - self.epoch
        self.assertIsInstance(result, DateTime)
        self.assertEqual(result.day, 31)

    def test_datetime_conversion(self):
        dtime = datetime.utcnow()
        new_dtime = DateTime.convert(dtime)
        self.assertIsInstance(new_dtime, DateTime)

    def test_datetime_conversion_idempotence(self):
        result = DateTime.convert(self.now)
        self.assertIsInstance(result, DateTime)
        self.assertEqual(self.now, result)

    def test_seconds_from_epoch(self):
        tstamp = self.now.seconds_from_epoch
        self.assertIsInstance(tstamp, float)

    def _test_timestamp_template(self, stamp, has_microseconds=False):
        self.assertIsInstance(stamp, basestring)
        self.assertEqual(len(stamp.split('-')), 3)
        self.assertTrue('T' in stamp)
        self.assertTrue('Z' in stamp)
        date, time = stamp.split('T')
        time = time.strip('Z')
        hour, minute, seconds = time.split(':')
        if has_microseconds:
            self.assertTrue('.' in seconds)

    def test_timestamp_to_seconds(self):
        stamp = self.now.timestamp()
        self.assertIsInstance(stamp, float)

    def test_timestamp_to_iso8601(self):
        stamp = self.now.timestamp(template=ISO_8601)
        self.assertEqual(self.now.iso8601, stamp)
        self._test_timestamp_template(stamp, has_microseconds=True)

    def test_timestamp_to_rfc3339(self):
        stamp = self.now.timestamp(template=RFC_3339)
        self.assertEqual(self.now.rfc3339, stamp)
        self._test_timestamp_template(stamp)

    def test_past_timestamp_to_seconds(self):
        stamp = self.now.past_timestamp(days=1)
        self.assertIsInstance(stamp, float)

    def test_past_timestamp_to_iso8601(self):
        stamp = self.now.past_timestamp(days=1, template=ISO_8601)
        self._test_timestamp_template(stamp, has_microseconds=True)

    def test_past_timestamp_to_rfc3339(self):
        stamp = self.now.past_timestamp(days=1, template=RFC_3339)
        self._test_timestamp_template(stamp)

    def test_datetime_playground(self):
        dtime = datetime(1970, 1, 2)
        self.assertEqual(dtime.hour, 0)
        self.assertEqual(dtime.minute, 0)
        self.assertEqual(dtime.microsecond, 0)
