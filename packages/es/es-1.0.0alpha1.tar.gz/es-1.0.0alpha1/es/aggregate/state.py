

class AggregateState:
    """Manages the state of an aggregate."""

    def __init__(self, aggregate, opts):
        self.__aggregate = aggregate
        self.__opts = opts
        self.__state = {}
        self.__version = 0
        self.__uncommitted = []
        self.__invalid = False

    def pop(self):
        """Return the first uncommitted event and removed it
        from the list.
        """
        return self.__uncommitted.pop(0)

    def is_dirty(self):
        """Return a boolean indicating if there are uncommitted
        events.
        """
        return bool(self.__uncommitted)

    def get_version(self):
        return self.__version

    def put_event(self, version, event):
        """Put an event in the uncommitted list.

        Args:
            version: the version of the aggregate that produced
                the event.
            event: the :class:`es.Event` instance.
        """
        assert version not in self.__uncommitted
        self.__uncommitted.append((version, event))

    def is_valid(self):
        """Return a boolean indicating if the state is valid."""
        return not self.__invalid

    def mark_invalid(self):
        """Mark the aggregate state as invalid."""
        self.__invalid = True

    def __setattr__(self, attname, value):
        if attname.startswith('_'):
            return super(AggregateState, self).__setattr__(attname, value)

        if not self.__opts.is_valid_field(attname):
            raise AttributeError(attname)
        self.__state[attname] = value

    def __getattr__(self, attname):
        if attname.startswith('_'):
            return super(AggregateState, self).__getattr__(attname)

        if not self.__opts.is_valid_field(attname):
            raise AttributeError(attname)
        return self.__state.get(attname)

    def increment_version(self):
        """Increments the aggregate version."""
        self.__version += 1
