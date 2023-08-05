import es


class FooSet(es.Event):
    value = es.fields.Integer(required=True)


class MultiEventHandler1(es.Event):
    pass


class MultiEventHandler2(es.Event):
    pass


class TestAggregate(es.Aggregate):
    foo = es.fields.Integer()
    multi1 = es.fields.Boolean(missing=False)
    multi2 = es.fields.Boolean(missing=False)

    @es.publishes
    def set_foo(self, value):
        yield FooSet(value=value)

    @es.publishes
    def multi1_emit(self):
        yield MultiEventHandler1()

    @es.publishes
    def multi2_emit(self):
        yield MultiEventHandler2()

    @es.handles(FooSet)
    def handle(self, state, event_class, event):
        state.foo = event.value

    @es.handles(MultiEventHandler1)
    @es.handles(MultiEventHandler2)
    def handle_multiple(self, state, event_class, event):
        if event_class == MultiEventHandler1:
            state.multi1 = True

        if event_class == MultiEventHandler2:
            state.multi2 = True
