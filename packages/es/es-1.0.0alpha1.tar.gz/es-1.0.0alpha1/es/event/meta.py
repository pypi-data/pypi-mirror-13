from es.fields import Field
from es.fields import Adapter


class EventMeta(type):
    ProgrammingError = type('ProgrammingError', (Exception,), {})
    RESERVED_ATTRS = set(['event_class','_adapter_class','_adapter','_data'])

    def __new__(cls, name, bases, attrs):
        super_new = super(EventMeta, cls).__new__
        if name == 'Event':
            return super_new(cls, name, bases, attrs)

        fields = {}
        for attname, value in list(attrs.items()):
            if attname in cls.RESERVED_ATTRS:
                raise cls.ProgrammingError("Reserved attribute: " + attname)

            if issubclass(type(value), Field):
                fields[attname] = attrs.pop(attname)

        attrs['_adapter_class'] = type(name + 'Adapter', (Adapter,), fields)
        attrs['_adapter'] = attrs['_adapter_class']()

        return super_new(cls, name, bases, attrs)
