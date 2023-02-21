import requests
from dotenv import dotenv_values
cookie_conf = dotenv_values('.env')

# region constants
DOMAIN = 'https://music.yandex.ru/api'
API_VERSION = 'v2.1'
PLAYLIST_OF_THE_DAY_PATH = 'handlers/playlist/503646255'
USER_ID = 26932097
HEADERS = {
    'Accept': 'application/json; q=1.0, text/*; q=0.8, */*; q=0.1',
    'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8,ja;q=0.7',
    # 'Connection': 'keep-alive'
    'X-Current-UID': cookie_conf['X-Current-UID'],
    'Cookie': cookie_conf['Cookie'],
    'X-Retpath-Y': 'https%3A%2F%2Fmusic.yandex.ru%2Fhome'
}
# endregion


class Album:
    def __init__(self, album_info):
        self.title = album_info['title']

    def __str__(self):
        return self.title


class Artist:
    def __init__(self, artist_info):
        self.name = artist_info['name']

    def __str__(self):
        return self.name


class Track:
    def __init__(self, track_info):
        self.title = track_info['title']
        self.artists = self.get_artists(self, track_info=track_info)
        self.albums = self.get_albums(self, track_info=track_info)

    @staticmethod
    def get_artists(self, track_info):
        artists = []
        for artist in track_info['artists']:
            artists.append(Artist(artist))
        return artists

    @staticmethod
    def get_albums(self, track_info):
        albums = []
        for album in track_info['albums']:
            albums.append(Album(album))
        return albums

    def __str__(self):
        return f'name: {self.title}, artists: {self.artists[0]}, album: {self.albums[0]}'


def process_yamusic_playlist(headers, user_id, playlist_id=PLAYLIST_OF_THE_DAY_PATH):
    raw_response = requests.get(url=f'{DOMAIN}/{API_VERSION}/{playlist_id}/{user_id}', headers=headers)
    raw_response_json = raw_response.json()
    tracks_raw = raw_response_json['tracks']
    tracks_pretty = []
    for track in tracks_raw:
        tracks_pretty.append(Track(track))

    return tracks_pretty


tracks = process_yamusic_playlist(headers=HEADERS, user_id=USER_ID)

for track in tracks:
    print(track)
