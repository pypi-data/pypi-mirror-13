import collections
import functools
import inspect
import types
import warnings

from es.event import Event


class EventPublisher:
    """The :class:`EventPublisher` publishes events locally to the
    aggregates in which they were published.
    """
    _handlers = collections.defaultdict(list)
    MissingEventHandler = type('MissingEventHandler', (LookupError,), {})
    VersionMismatch = type('VersionMismatch', (Exception,), {})

    def __init__(self):
        self._events = {}

    def publish(self, aggregate, state, event, replay=False, version=None):
        """Publishes an event within the scope of the given `aggregate`."""
        current_version = state.get_version()
        handlers = self._handlers[type(event)]
        if not handlers:
            warnings.warn("No handlers found for " + type(event).__name__)

        for handler in handlers:
            handler(aggregate, aggregate._state, type(event), event)
            state.increment_version()

            # If the `version` parameter was provided, this means that events
            # are being replayed. The provided version must match the aggregates
            # previous version.
            if (version is not None) and (version != current_version):
                raise self.VersionMismatch

        # If not replaying, add the event to the uncommitted list, indicating
        # that it has to be persisted to the data store.
        if not replay:
            state.put_event(current_version, event)

    def add_handler(self, func, event_classes):
        """Registers a handler function for a list of :class:`Event`
        classes.
        """
        for event_class in event_classes:
            self._events[event_class.event_type] = event_class
            self._handlers[event_class].append(func)


class EventHandler:
    """Wraps the event handling functions."""

    def __init__(self, event_class):
        self.event_classes = [event_class]
        self.func = None
        self.publisher = None

    def add_to_publisher(self, publisher):
        """Adds the event handler to a :class:`EventPublisher`."""
        assert self.publisher is None
        assert self.func is not None
        self.publisher = publisher
        publisher.add_handler(self.func, self.event_classes)

    def decorate(self, obj):
        # Decorate might be invoked using a function as its argument,
        # or an event class.
        if isinstance(obj, EventHandler):
            self.event_classes.extend(obj.event_classes)
            self.func = obj.func
        else:
            # This is the function handling the event(s)
            self.func = obj
        return self


def publishes(func):
    """A method decorator indicating that the specified method
    publishes events.
    """
    @functools.wraps(func)
    def f(self, *args, **kwargs):
        if not self._state.is_valid():
            raise self.InvalidState
        for event in func(self, *args, **kwargs):
            if not event:
                continue
            try:
                self.apply_event(event)
            except Exception as e:
                # The event handler has failed to execute the event. Mark the
                # state as inconsistent so the consumer is forced to reload the
                # aggregate from a valid state.
                self._state.mark_invalid()
                raise

    return f


def handles(event_class):
    """Method decorator that registers a handler function for an event
    published within an aggregate.
    """
    handler = EventHandler(event_class)
    return handler.decorate
