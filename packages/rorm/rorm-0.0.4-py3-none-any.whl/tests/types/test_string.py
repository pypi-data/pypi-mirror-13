import unittest
import string
import itertools

from factory.fuzzy import FuzzyText, FuzzyInteger

from ..services import Redis

from rorm.client import Client
from rorm.types import String


rlen = FuzzyInteger(10, 50).fuzz()  # used as string length
rs = FuzzyText().fuzz()  # random string
rpi = FuzzyInteger(1, rlen - 1).fuzz()  # random positive integer
rni = FuzzyInteger(-rlen, -1).fuzz()  # random negative integer
rpio = FuzzyInteger(rlen, 2 * rlen).fuzz()  # random positive integer, out of range
rnio = FuzzyInteger(-2 * rlen, -(rlen + 1)).fuzz()  # random negative integer, out of range
rstr = FuzzyText(length=rlen, chars=string.printable).fuzz()  # random string with random length


def setUpModule():
    Client.instance = Redis('test-service-string')
    Client.get_client().flushall()
    global rstring
    rstring = String(rstr)  # redis string type


def tearDownModule():
    Client.get_client().flushall()
    Client.instance.stop()


class GetItemSpecialMethodTestCase(unittest.TestCase):
    """
    Test String.__getitem__ method
    """

    def test_invalid_index_values(self):
        self.assertRaises(ValueError, lambda: rstring[::0])
        self.assertRaises(TypeError, lambda: rstring[None])
        self.assertRaises(TypeError, lambda: rstring[rs])
        self.assertRaises(IndexError, lambda: rstring[rpio])
        self.assertRaises(IndexError, lambda: rstring[rnio])

    def test_single_index_value(self):
        possible_indice_values = (rpi, rni, -1, 1, 0)
        for key in possible_indice_values:
            with self.subTest(key=key):
                self.assertEqual(rstr[key].encode(), rstring[key])

    def test_slice_values_combinations(self):
        """
        Tests all possible combinations of three argument slice
        """

        possible_step_values = (rpi, rpio, rni, rnio, None)

        possible_indice_values = (rpi, rni, rpio, rnio, 0, None)

        possible_start_stop_slices = tuple(  # possible two arg slices [start:stop]
            itertools.product(possible_indice_values, repeat=2))

        possible_start_stop_step_slices = tuple(  # possible three arg slices [start:stop:step]
            itertools.product(possible_start_stop_slices, possible_step_values))

        for indices, step in possible_start_stop_step_slices:
            slice_ = slice(*indices, step)
            with self.subTest(slice_=slice_):
                self.assertEqual(rstr[slice_].encode(), rstring[slice_])


class LenSpecialMethodTestCase(unittest.TestCase):

    def test___len___method_output(self):
        self.assertEqual(len(rstr), len(rstring))
        self.assertEqual(len(rstr), rlen)


class StrSpecialMethodTestCase(unittest.TestCase):

    def test___str___method_output(self):
        self.assertEqual(str(rstr.encode()), rstring.__str__())


class ContainsSpecialMethodTestCase(unittest.TestCase):

    def test_in_operator_using_whole_string(self):
        self.assertIn(rstr.encode(), rstring)

    def test_in_operator_using_string_fragment(self):
        self.assertIn(rstr[rpi:-rni].encode(), rstring)


class ReversedSpecialMethodTestCase(unittest.TestCase):

    def test_order_of_char_after_using_reversed_method(self):
        for rev_rstr, rev_rstring in zip(reversed(rstr), reversed(rstring)):
            with self.subTest(rev_rstr=rev_rstr, rev_rstring=rev_rstring):
                self.assertEqual(rev_rstr.encode(), rev_rstring)


class CountMethodTestCase(unittest.TestCase):

    def test_count_with_every_char_in_string(self):
        for char in rstr:
            with self.subTest(char=char):
                self.assertEqual(
                    rstr.count(char),
                    rstring.count(char.encode()))

    def test_count_with_random_slice(self):
        rsli = rstr[rpi:-rni]
        self.assertEqual(
            rstr.count(rsli),
            rstring.count(rsli.encode()))


class IndexMethodTestCase(unittest.TestCase):

    def test_index_with_every_char_in_string(self):
        for char in rstr:
            with self.subTest(char=char):
                self.assertEqual(
                    rstr.index(char),
                    rstring.index(char.encode()))

    def test_index_with_random_slice(self):
        rsli = rstr[rpi:-rni]
        self.assertEqual(
            rstr.index(rsli),
            rstring.index(rsli.encode()))

    def test_index_with_non_existent_fragment(self):
        nonex = '\0'
        self.assertNotIn(nonex.encode(), rstring)
        self.assertRaises(
            ValueError, lambda: rstring.index(nonex))

test_cases = (
    IndexMethodTestCase,
    CountMethodTestCase,
    ReversedSpecialMethodTestCase,
    ContainsSpecialMethodTestCase,
    StrSpecialMethodTestCase,
    LenSpecialMethodTestCase,
    GetItemSpecialMethodTestCase,
)


def load(loader, test_cases):
    suite = unittest.TestSuite()
    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


def run():
    return load(unittest.defaultTestLoader, test_cases)
