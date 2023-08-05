import unittest
from unittest import TestCase

from sqlitelist.wrapper import open as sqopen


class SqliteListTests(TestCase):
    def test_append(self):
        with sqopen(':memory:') as l:
            l.append('string')
            l.append(['list', 'with', 1, {'hello': set()}])
            l.append(2413245)
            self.assertEqual(len(l), 3)
            self.assertEqual(l[0], 'string')
            self.assertEqual(l[1], ['list', 'with', 1, {'hello': set()}])
            self.assertEqual(l[2], 2413245)
            self.assertEqual(l[-1], 2413245)

    def test_extend(self):
        with sqopen(':memory:') as l:
            l.extend(['asdf', [], {}, 4])
            self.assertEqual(len(l), 4)
            self.assertEqual(l[0], 'asdf')
            self.assertEqual(l[2], {})
            self.assertEqual(l[-2], {})

    def test_slice(self):
        with sqopen(':memory:') as l:
            seq = list(range(20))
            l.extend(seq)
            self.assertEqual(l[0:2], seq[0:2])
            self.assertEqual(l[0:5], seq[0:5])
            self.assertEqual(l[:5], seq[:5])
            with self.assertRaises(IndexError):
                l[::2]
            self.assertEqual(l[2:], seq[2:])
            with self.assertRaises(TypeError):
                l[2.34]
            with self.assertRaises(IndexError):
                l[5000]
            self.assertEqual(l[200:], [])

    def test_setitem(self):
        with sqopen(':memory:') as l:
            l.extend([1, 2, 3, 4])
            l[0] = 'override'
            self.assertEqual(list(l), ['override', 2, 3, 4])
            l[-1] = 'override'
            self.assertEqual(list(l), ['override', 2, 3, 'override'])
            l[-2] = 'hello'
            self.assertEqual(list(l), ['override', 2, 'hello', 'override'])
            l[2] = 'world'
            self.assertEqual(list(l), ['override', 2, 'world', 'override'])
            with self.assertRaises(IndexError):
                l[5] = 'hello'
                l[4] = 'hello'

    def test_iteration(self):
        with sqopen(':memory:') as l:
            seq = list(range(20))
            l.extend(seq)
            temp = []
            for i in l:
                temp.append(i)
            self.assertEqual(temp, seq)

    def test_flush(self):
        with sqopen(':memory:') as l:
            l.extend(list(range(200)))
            l.flush()
            self.assertEqual(len(l), 0)

    def test_pop(self):
        with sqopen(':memory:') as l:
            seq = list(range(20))
            l.extend(seq)
            el = l.pop(0)
            self.assertEqual(el, 0)
            el = l.pop()
            self.assertEqual(el, 19)
            el = l.pop(5)
            self.assertEqual(el, 6)
            seq.pop(0)
            seq.pop()
            seq.pop(5)
            self.assertEqual(list(l), seq)

    def test_delete(self):
        with sqopen(':memory:') as l:
            l.extend([1, 2, 3])
            del l[0]
            self.assertEqual(list(l), [2, 3])
            del l[-1]
            self.assertEqual(list(l), [2])
            del l[0]
            l.extend([1, 2, 3, 4, 5])
            del l[2]
            self.assertEqual(list(l), [1, 2, 4, 5])

    def test_delete_slice(self):
        with sqopen(':memory:') as l:
            seq = list(range(20))
            l.extend(seq)
            del l[:5]
            del seq[:5]
            self.assertEqual(list(l), seq)
            del l[2:3]
            del seq[2:3]
            self.assertEqual(list(l), seq)
            del l[5:]
            del seq[5:]
            self.assertEqual(list(l), seq)

    def test_bool(self):
        with sqopen(':memory:') as l:
            self.assertEqual(bool(l), False)
            l.append('hello')
            self.assertEqual(bool(l), True)


if __name__ == '__main__':
    unittest.main()
