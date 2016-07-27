from kivy.event import EventDispatcher


class UiEventBus(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type("on_add")
        self.register_event_type("on_load_list")
        # self.register_event_type("on_delete")
        # self.register_event_type("on_start")
        # self.register_event_type("on_failed")
        super(EventDispatcher, self).__init__(**kwargs)

    def load_list(self, value):
        self.dispatch("on_load_list", value)

    def add_track(self, value):
        self.dispatch("on_add", value)

    def on_load_list(self, *args):
        print "On load list"

    def on_add(self, *args):
        print "Event dispatcher on add"
