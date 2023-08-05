from es.aggregate.options import AggregateOptions
from es.publisher import EventPublisher
from es.publisher import EventHandler
from es.fields import Field


class AggregateMeta(type):
    ProgrammingError = type('ProgrammingError', (Exception,), {})

    def __new__(cls, name, bases, attrs):
        super_new = super(AggregateMeta, cls).__new__
        if name == 'Aggregate':
            return super_new(cls, name, bases, attrs)

        attrs['_publisher'] = publisher = EventPublisher()
        attrs['_meta'] = meta = AggregateOptions(attrs.pop('Meta', None))
        for attname, value in list(attrs.items()):
            if issubclass(type(value), Field):
                meta.add_field(attname, value)
                del attrs[attname]

            if isinstance(value, EventHandler):
                value.add_to_publisher(publisher)
                del attrs[attname]

        return super_new(cls, name, bases, attrs)

    def add_to_class(self, attname, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(attname, self)
        else:
            setattr(self, attname, value)
