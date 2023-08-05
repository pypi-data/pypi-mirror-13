from twisted.trial.unittest import TestCase
from ngen.utils import cached_property, chunk


class Thing(object):

    multiplier = 0

    def __init__(self, multiplier):
        self.multiplier = multiplier

    @cached_property
    def stuff(self):
        return self.multiplier * 3


class UtilsTests(TestCase):

    def setUp(self):
        self.instance = Thing(4)

    def test_cached_property(self):
        self.assertTrue('stuff' not in self.instance.__dict__)

        self.assertTrue('stuff' in dir(self.instance))

        getattr(self.instance, 'stuff')

        self.assertTrue('stuff' in self.instance.__dict__)

        self.instance.__dict__['stuff'] = 'aha!'

        # this means that once the initial function is called the function name
        # and its output are added to the instance's __dict__ which takes
        # precedent over the decorated function.
        self.assertEqual(self.instance.stuff, 'aha!')

        del self.instance.__dict__['stuff']

        # this means that deleting the function name from the set of keys in
        # the instance's __dict__ you have effectively busted the cache.
        self.assertEqual(self.instance.stuff, 12)

    def test_chunk(self):

        array = range(10)
        chunky = chunk(array, 2)

        self.assertEqual(len(chunky), 5)

        self.assertEqual(len(chunky[0]), 2)
        self.assertEqual(len(chunky[-1]), 2)

        chunky = chunk(array, 3)
        self.assertEqual(len(chunky), 4)

        self.assertEqual(len(chunky[0]), 3)
        self.assertEqual(len(chunky[-1]), 1)

        chunky = chunk(array, 3, strict=True)
        self.assertEqual(len(chunky), 3)

        self.assertEqual(len(chunky[0]), 3)
        self.assertEqual(len(chunky[-1]), 3)

        chunky = chunk(tuple(array), 3, strict=True)
        self.assertEqual(len(chunky), 3)

        self.assertEqual(len(chunky[0]), 3)
        self.assertEqual(len(chunky[-1]), 3)
