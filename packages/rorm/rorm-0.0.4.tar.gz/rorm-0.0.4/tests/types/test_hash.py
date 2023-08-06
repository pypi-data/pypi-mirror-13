import unittest
from ..services import Redis

from rorm.client import Client
from rorm.types import Hash


class HashTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Client.instance = cls.service = Redis('test-service-hash')
        cls.client = cls.service.get_client()
        cls.client.flushall()

    @classmethod
    def tearDownClass(cls):
        cls.client.flushall()
        cls.service.stop()

    def setUp(self):
        self.dragon_red = Hash()  # uses auto generated key
        self.dragon_black = Hash(
            key='custom-key-3442-24 423@#&^$!_*?><|\;')

    def test_hash_with_auto_key(self):
        import uuid
        self.assertIsInstance(self.dragon_black.key, str)
        self.assertEqual(len(self.dragon_black.key), len(str(uuid.uuid4())))
        self.assertNotEqual(self.dragon_black.key, self.dragon_red.key)

    def test_hash_with_custom_key(self):
        self.assertEqual(
            self.dragon_black.key, 'custom-key-3442-24 423@#&^$!_*?><|\;')

    def test_hash_wrong_initial_data(self):
        self.assertRaises(ValueError, Hash, tuple)
        self.assertRaises(ValueError, Hash, 4)

    def test_type_of_object(self):
        self.assertIsInstance(self.dragon_red, Hash)

    def test_length_of_object(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344})

        self.assertEqual(len(dragon_blue), 3)

    def test_get_string_data(self):
        self.dragon_red['name'] = 'Dormith Champion Of The Red'
        self.dragon_black['name'] = 'Jeruth Lord Of The Black'
        self.dragon_red['element'] = 'fire'

        self.assertEqual(
            self.dragon_red['name'], b'Dormith Champion Of The Red')
        self.assertEqual(
            self.dragon_black['name'], b'Jeruth Lord Of The Black')
        self.assertEqual(self.dragon_red['element'], b'fire')

    def test_get_int_data(self):
        self.dragon_red['age'] = 23489
        self.dragon_black['age'] = 89239
        self.assertEqual(self.dragon_red['age'], b'23489')
        self.assertEqual(self.dragon_black['age'], b'89239')

    def test_get_raw_data(self):
        self.dragon_red['real_name'] = '!@#$%^&*()_+{}:"<>?`\`"'
        self.dragon_black['real_name'] = '!()00&*()_+{}:"<>?`\`"'
        self.assertEqual(
            self.dragon_red['real_name'], b'!@#$%^&*()_+{}:"<>?`\`"')
        self.assertEqual(
            self.dragon_black['real_name'], b'!()00&*()_+{}:"<>?`\`"')

    def test_clear_method(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344})

        self.assertEqual(len(dragon_blue), 3)
        dragon_blue.clear()
        self.assertEqual(len(dragon_blue), 0)
        self.assertEqual(dragon_blue, {})

    def test_items_method(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344}
        )

        self.assertCountEqual(
            dragon_blue.items(),
            ((b'name', b'Lusarth The Powerful One'),
                (b'element', b'ice'),
                (b'age', b'123344'))
        )

    def test_keys_method(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344}
        )

        self.assertCountEqual(
            dragon_blue.keys(),
            (b'name', b'element', b'age',))

    def test_pop_method(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344}
        )

        self.assertEqual(
            dragon_blue.pop('name'),
            b'Lusarth The Powerful One'
        )
        self.assertEqual(
            dragon_blue.pop('element'),
            b'ice'
        )
        self.assertEqual(
            dragon_blue.pop('age'),
            b'123344'
        )

    def test_popitem_method(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344}
        )
        self.assertCountEqual(
            (
                dragon_blue.popitem(),
                dragon_blue.popitem(),
                dragon_blue.popitem()
            ),
            (
                (b'name', b'Lusarth The Powerful One'),
                (b'age', b'123344'),
                (b'element', b'ice')
            )
        )

        self.assertRaises(
            KeyError,
            dragon_blue.popitem
        )

    def test_setdefault_method(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344}
        )
        self.assertEqual(
            dragon_blue.setdefault('weight', 'heavy'),
            'heavy'
        )
        self.assertDictEqual(
            dict(dragon_blue),
            {
                b'name': b'Lusarth The Powerful One',
                b'weight': b'heavy',
                b'element': b'ice',
                b'age': b'123344'
            }
        )

    def test_update_method(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344}
        )

        dragon_blue.update({'height': 'big', 'length': 'long'})

        self.assertDictEqual(
            dict(dragon_blue),
            {
                b'name': b'Lusarth The Powerful One',
                b'element': b'ice',
                b'age': b'123344',
                b'height': b'big',
                b'length': b'long'
            }
        )

    def test_values_method(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344}
        )
        self.assertCountEqual(
            dragon_blue.values(),
            (b'Lusarth The Powerful One', b'ice', b'123344')
        )

    def test___str___method(self):
        dragon_blue = Hash({
            'name': 'Lusarth The Powerful One',
            'element': 'ice',
            'age': 123344}
        )

        self.assertCountEqual(
            dragon_blue.__str__(),
            "{b'name': b'Lusarth The Powerful One', "
            "b'element': b'ice', "
            "b'age': b'123344'}"
        )
