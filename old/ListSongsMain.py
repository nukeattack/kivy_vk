from Canvas import Line, Rectangle

from kivy.app import App
from kivy.atlas import CoreImage
from kivy.graphics.context_instructions import Color
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from kivy.graphics import Color, Rectangle

# VK
TOKEN = "90f4ee1ddf5ae8842f6a26870f7be56b73fe700980f0f066bf7ac3eb3e1778786f0d09c0d9cd2ffb9bd76"
USER_ID = "11861303"

import webbrowser
import pickle
import json
import urllib
import urllib2
import HTMLParser
import re
import os
import urlparse
from datetime import datetime, timedelta

# id of vk.com application, that has access to audio
import time

APP_ID = '5163868'
# if None, then save mp3 in current folder
MUSIC_FOLDER = 'music'
# file, where auth data is saved
AUTH_FILE = '.auth_data'
# chars to exclude from filename
FORBIDDEN_CHARS = '/\\\?%*:|"<>!'


def get_saved_auth_params():
    access_token = None
    user_id = None
    try:
        with open(AUTH_FILE, 'rb') as pkl_file:
            token = pickle.load(pkl_file)
            expires = pickle.load(pkl_file)
            uid = pickle.load(pkl_file)
        if datetime.now() < expires:
            access_token = token
            user_id = uid
    except IOError:
        pass
    return access_token, user_id


def save_auth_params(access_token, expires_in, user_id):
    expires = datetime.now() + timedelta(seconds=int(expires_in))
    with open(AUTH_FILE, 'wb') as output:
        pickle.dump(access_token, output)
        pickle.dump(expires, output)
        pickle.dump(user_id, output)


def get_auth_params():
    auth_url = ("https://oauth.vk.com/authorize?client_id={app_id}"
        "&scope=audio&redirect_uri=https://oauth.vk.com/blank.html"
        "&display=page&response_type=token".format(app_id=APP_ID))
    webbrowser.open_new_tab(auth_url)
    redirected_url = raw_input("Paste here url you were redirected:\n")
    aup = urlparse.parse_qs(redirected_url)
    aup['access_token'] = aup.pop(
        'https://oauth.vk.com/blank.html#access_token')
    save_auth_params(aup['access_token'][0], aup['expires_in'][0],
        aup['user_id'][0])
    return aup['access_token'][0], aup['user_id'][0]


def get_tracks_metadata(access_token, user_id):
    url = ("https://api.vkontakte.ru/method/audio.get.json?"
        "uid={uid}&access_token={atoken}".format(
            uid=user_id, atoken=access_token))
    audio_get_page = urllib2.urlopen(url).read()
    return json.loads(audio_get_page)['response']


def get_track_full_name(t_data):
    html_parser = HTMLParser.HTMLParser()
    full_name = u"{0}_{1}".format(
        html_parser.unescape(t_data['artist'][:100]).strip(),
        html_parser.unescape(t_data['title'][:100]).strip(),
    )
    full_name = re.sub('[' + FORBIDDEN_CHARS + ']', "", full_name)
    full_name = re.sub(' +', ' ', full_name)
    return full_name + ".mp3"


def download_track(t_url, t_name):
    t_path = os.path.join(MUSIC_FOLDER or "", t_name)
    max_retry = 2
    if not os.path.exists(t_path):
        retry_count = 0
        while retry_count < max_retry:
            try:
                print "Downloading {0}".format(t_name.encode('ascii', 'replace'))
                urllib.urlretrieve(t_url, t_path)
                break;
            except:
                retry_count += 1


#--
# def main():
#     access_token, user_id = get_saved_auth_params()
#     tracks_downloaded = 0
#     download_delay_frequency = 25
#     sleep_length = 60
#     if not access_token or not user_id:
#         access_token, user_id = get_auth_params()
#     tracks = get_tracks_metadata(access_token, user_id)
#     if MUSIC_FOLDER and not os.path.exists(MUSIC_FOLDER):
#         os.makedirs(MUSIC_FOLDER)
#     for t in tracks:
#         t_name = get_track_full_name(t)
#         tracks_downloaded += 1
#         download_track(t['url'], t_name)
#         if tracks_downloaded % download_delay_frequency == 0:
#             print "Sleep % sec" % sleep_length
#             time.sleep(sleep_length)
#     print "All music is up to date"

#------------------------------------------------------------------------------------------------------- VK

class TrackRecord:
    def __init__(self):
        self.label = "Track label"

class TrackList:
    def __init__(self):
        self.tracks = []


class DownloadManager:
    def __init__(self):
        pass

    def add_task(self):
        pass


def draw(instance, value):
    instance.rect.pos = instance.pos
    instance.rect.size = (200, 20)

class SongEntry(GridLayout):
    progress = 0

    def __init__(self, artist, title, **kwargs):
        super(SongEntry, self).__init__(**kwargs)
        self.cols = 2
        self.rows = 2
        self.track_artist = Label(text=artist)
        self.track_title = Label(text=title)
        self.progress = ProgressBar(max=100)
        self.progress.value = 20
        self.add_widget(self.track_artist)
        self.add_widget(self.track_title)
        self.add_widget(self.progress)
        self.bind(pos=draw, size=draw)



class SongListLayout(GridLayout):
    def __init__(self, **kwargs):
        super(SongListLayout, self).__init__(**kwargs)
        self.width = 500
        self.cols = 1
        self.spacing = 1
        self.orientation = "vertical"
       # self.bind(minimum_height=self.setter('height'))
        # songs = get_tracks_metadata(TOKEN, USER_ID)

        # for song in songs:
        # for song in songs:
        #     # song = {"artist":"artist", "title": "title"}
        #     self.add_widget(SongWidget(song["artist"], song["title"], size_hint_y=None, height=40))
        #

        for i in xrange(5):
            # song = {"artist":"artist", "title": "title"}
            self.add_widget(SongEntry("artist", "title", size_hint_y=None, height=40))


class SongListScroll(ScrollView):
    def __init__(self, **kwargs):
        super(SongListScroll, self).__init__(**kwargs)
        self.add_widget(SongListLayout(size_hint=(None, None)))

class ListSongsApp(App):
    def build(self):
        # return SongListScroll()
        return SongListLayout( )

if __name__ == "__main__":
    ListSongsApp().run()
