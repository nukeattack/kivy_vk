from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from track_processing import TrackDownloader
from v2.UiEventBus import UiEventBus

event_dispatcher = UiEventBus()

class TrackRecord:
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title


class DownloadManager:
    def __init__(self):
        self.tracks = []


class SongWidget(GridLayout):
    artist_name = StringProperty("artistname")
    track_title = StringProperty("tracktitle")

    def __init__(self, **kwargs):
        super(SongWidget, self).__init__(**kwargs)

    def on_click(self, *args):
        print


class SongList(GridLayout):
    def __init__(self, **kwargs):
        super(SongList, self).__init__(**kwargs)
        self.event_dispatcher = event_dispatcher
        self.bind(minimum_height=self.setter('height'))
        self.event_dispatcher.bind(on_add=self.add_track)

    def add_track(self, *args):
        track = args[1]
        self.add_widget(SongWidget(size_hint=(None, None), artist_name=track.artist, track_title=track.title))


class SongScroll(ScrollView):
    pass


class RootWidget(GridLayout):
    def __init__(self, event_dispatcher, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.event_dispatcher = event_dispatcher


class SongList2App(App):
    def build(self):
        self.event_dispatcher = UiEventBus()
        self.track_downloader = TrackDownloader(event_dispatcher)
        Clock.schedule_once(lambda x: event_dispatcher.load_list(1), 3)
        return RootWidget(self.event_dispatcher)


if __name__ == "__main__":
    SongList2App().run()
