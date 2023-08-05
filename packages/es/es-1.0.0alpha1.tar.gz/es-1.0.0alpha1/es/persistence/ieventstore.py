

class IEventStore:
    """Specifies the basic interface for an event store,
    the backend used to persist events.
    """
    default_user = 1
    default_service = 1
    ConcurrencyException = type('ConcurrencyException', (Exception,), {})

    def load(self, aggregate_class, aggregate_id):
        """Loads the aggregate of class `aggregate_class` from the persistence
        backend, identified by `aggregrate_id`.
        """
        agg = aggregate_class(aggregate_id=aggregate_id)
        for version, event in self.get_events(agg):
            agg.apply_event(event, version=version, replay=True)

        return agg

    def get_events(self, agg):
        """Load all events for the given :class:`es.Aggregate` `agg` from
        the persistence backend.
        """
        raise NotImplementedError("Subclasses must override this method.")

    def persist_aggregate(self, aggregate, user_id=None, service_id=None):
        """Persist all uncommitted events in an aggregate to the data
        store.
        """
        for version, event in aggregate.get_uncommitted():
            self.persist_event(aggregate.aggregate_id, version,
                event, user_id=user_id,
                service_id=service_id)

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
        raise NotImplementedError("Subclasses must override this method.")

    def get_default_user(self):
        """Return the identifier of the default user."""
        return self.default_user

    def get_default_service(self):
        """Return the identifier of the default service."""
        return self.default_service
