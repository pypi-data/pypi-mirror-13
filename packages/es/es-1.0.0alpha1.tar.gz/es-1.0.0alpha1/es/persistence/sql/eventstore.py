from libsousou.meta import hybrid_property
import ioc

from es.persistence.ieventstore import IEventStore
from es.persistence.sql.orm import Source
from es.persistence.sql.orm import Event


class EventStore(IEventStore):
    """An SQLAlchemy implementation of the event store."""
    source_model = Source
    event_model = Event
    session_factory = ioc.instance('es:sessionmaker')

    @hybrid_property
    def session(self):
        return self.session_factory()

    def persist_event(self, transaction_id, aggregate_id, event,
        user_id=None, service_id=None):
        """Persist an event in the storage backend. Return an unsigned long
        integer identifying the event.

        Args:
            transaction_id: identifies the transaction.
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
        dao = self.event_model(
            aggregate_id=aggregate_id,
            version=version,
            event_type=event.event_type,
            event_data=event.dump(),
            user_id=user_id if (user_id is not None)\
                else self.get_default_user(),
            service_id=service_id if (service_id is not None)\
                else self.get_default_user(),
            transaction_id=transaction_id
        )
        self.session.add(dao)
        self.session.flush()
        return dao.event_id
