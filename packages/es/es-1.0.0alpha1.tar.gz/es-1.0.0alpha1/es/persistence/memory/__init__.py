import collections

from es.persistence.ieventstore import IEventStore


class EventStore(IEventStore):
    __events = collections.defaultdict(list)

    def __init__(self, flush=False):
        self.__events = EventStore.__events\
            if not flush else collections.defaultdict(list)

    def get_events(self, agg):
        return self.__events[agg.aggregate_id]

    def persist_event(self, aggregrate_id, version, event,
        user_id=None, service_id=None, transaction_id=None):
        """Persist an event in the storage backend. Return an unsigned long
        integer identifying the event.

        Args:
            aggregrate_id: a string identifying the aggregate in which
                the event took place.
            version: the aggregate version that dispatched the event.
            event: the event.
            user_id: an unsigned long integer identifying the user that
                triggered the event.
            service_id: an unsigned long integer identifying the service
                through which the event was triggered.

        Returns:
            unsigned long integer
        """
        self.__events[aggregrate_id].append((version, event))
