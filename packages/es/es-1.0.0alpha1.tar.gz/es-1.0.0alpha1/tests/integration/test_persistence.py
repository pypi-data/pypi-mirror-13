import unittest

from es.persistence.memory import EventStore
from es.test import TestAggregate


class EventHandlingTestCase(unittest.TestCase):

    def setUp(self):
        self.store = EventStore(flush=True)
        self.agg = TestAggregate()
        self.state = self.agg._state

    def test_persist(self):
        self.agg.set_foo(1)
        self.store.persist_aggregate(self.agg)

    def test_load(self):
        self.agg.set_foo(1)
        self.store.persist_aggregate(self.agg)

        agg = self.store.load(TestAggregate, self.agg.aggregate_id)
        state = agg._state

        self.assertEqual(state.get_version(), self.state.get_version())
        self.assertEqual(state.foo, 1)


if __name__ == '__main__':
    unittest.main()
