import unittest

from es.test import TestAggregate


class EventHandlingTestCase(unittest.TestCase):

    def test_set_foo(self):
        agg = TestAggregate()
        state = agg._state
        self.assertEqual(state.foo, None)
        agg.set_foo(1)
        self.assertEqual(state.foo, 1)

    def test_multiple_decorated(self):
        agg = TestAggregate()
        state = agg._state
        self.assertFalse(state.multi1)
        self.assertFalse(state.multi2)

        agg.multi1_emit()
        self.assertTrue(state.multi1)
        self.assertFalse(state.multi2)

        agg = TestAggregate()
        state = agg._state
        agg.multi2_emit()
        self.assertFalse(state.multi1)
        self.assertTrue(state.multi2)


if __name__ == '__main__':
    unittest.main()
