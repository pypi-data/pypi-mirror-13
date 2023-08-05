import inspect

from libsousou.meta import hybrid_property

from es.event.meta import EventMeta


class Event(metaclass=EventMeta):

    @hybrid_property
    def event_type(cls):
        return (cls if inspect.isclass(cls) else type(cls)).__name__

    def __init__(self, **params):
        self._data = params

    def __getattr__(self, attname):
        try:
            return self._data[attname]
        except KeyError:
            raise AttributeError(attname)
