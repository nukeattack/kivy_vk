from v2.vk_track import VkTrack

# VK
TOKEN = "abf76d8bd848757f71ed108c5e17124f830ae3e69764b32b4caae0b2d5ed53844ecfac353141f81647e14"
USER_ID = "11861303"

import webbrowser
import pickle
import HTMLParser
import re
import urlparse
from datetime import datetime, timedelta

# id of vk.com application, that has access to audio

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
    # url = ("https://api.vkontakte.ru/method/audio.get.json?"
    #     "uid={uid}&access_token={atoken}".format(
    #         uid=user_id, atoken=access_token))
    # audio_get_page = urllib2.urlopen(url).read()
    # return json.loads(audio_get_page)['response']
    return [{"artist":"Artist name", "title":"Track title", "url":"url_to_track"}]


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
    print "Download track %s %s" % (t_url, t_name)
    # t_path = os.path.join(MUSIC_FOLDER or "", t_name)
    # max_retry = 2
    # if not os.path.exists(t_path):
    #     retry_count = 0
    #     while retry_count < max_retry:
    #         try:
    #             print "Downloading {0}".format(t_name.encode('ascii', 'replace'))
    #             urllib.urlretrieve(t_url, t_path)
    #             break;
    #         except:
    #             retry_count += 1


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


# def add_track():
#     print "Track added"


class TrackDownloader():
    def __init__(self, event_dispatcher):
        self.event_dispatcher = event_dispatcher
        self.event_dispatcher.bind(on_load_list=self.on_load_list)
        self.tracks = []

    def on_load_list(self, *args):
        tracks_metadata = get_tracks_metadata(TOKEN, USER_ID)
        print tracks_metadata
        print "Load list achieved"
        print self
        for track in tracks_metadata:
            self.add(track["url"], track["artist"], track["title"])

    def add(self, track_id, artist, title):
        track = VkTrack(track_id, artist, title)
        self.tracks.append(track)
        self.event_dispatcher.add_track(track)
