import oslotest.base

from kostyor_cli.commands.common import showarray, showone


class TestShowArray(oslotest.base.BaseTestCase):

    columns = (
        ('a', 'The A'),
        ('b', 'The B'),
    )

    def test_no_entries(self):
        expected = (['The A', 'The B'], [])
        self.assertEqual(expected, showarray([], self.columns))

    def test_one_entry(self):
        data = [
            {'a': 14, 'b': 42},
        ]
        expected = (
            ['The A', 'The B'],
            [[14, 42]],
        )
        self.assertEqual(expected, showarray(data, self.columns))

    def test_many_entries(self):
        data = [
            {'a': 14, 'b': 42},
            {'a': 10, 'b': 11},
            {'a': 90, 'b': 99},
        ]
        expected = (
            ['The A', 'The B'],
            [[14, 42],
             [10, 11],
             [90, 99]],
        )
        self.assertEqual(expected, showarray(data, self.columns))

    def test_plain_type(self):
        columns = ((None, 'The Label'), )
        data = [14, 42]
        expected = (
            ['The Label'],
            [[14],
             [42]],
        )
        self.assertEqual(expected, showarray(data, columns))


class TestShowOne(oslotest.base.BaseTestCase):

    columns = (
        ('a', 'The A'),
        ('b', 'The B'),
    )

    def test_one_entry(self):
        data = {'a': 13, 'b': 42}
        expected = (
            ['The A', 'The B'],
            [13, 42]
        )
        self.assertEqual(expected, showone(data, self.columns))
