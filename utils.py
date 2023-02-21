import json

import requests
from dotenv import dotenv_values

cookie_conf = dotenv_values('.env')

# region constants
YA_DOMAIN = 'https://music.yandex.ru/api'
YA_API_VERSION = 'v2.1'
YA_PLAYLIST_OF_THE_DAY_PATH = 'handlers/playlist/503646255'
USER_ID = 26932097
YA_HEADERS = {
    'Accept': 'application/json; q=1.0, text/*; q=0.8, */*; q=0.1',
    'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8,ja;q=0.7',
    # 'Connection': 'keep-alive'
    'X-Current-UID': cookie_conf['X-Current-UID'],
    'Cookie': cookie_conf['Cookie'],
    'X-Retpath-Y': 'https%3A%2F%2Fmusic.yandex.ru%2Fhome'
}

SPOTIFY_API_DOMAIN = 'https://api.spotify.com'
SPOTIFY_API_VERSION = 'v1'
SPOTIFY_API_SEARCH_PATH = 'search'
SPOTIFY_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': cookie_conf['Spotify-Bearer']
}
SPOTIFY_PLAYLIST_ID = cookie_conf['Spotify-playlist-id']



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

    def to_spotify_search_format(self):
        return f'track:{self.title} artist:{self.artists[0].name}'

    def __str__(self):
        return f'name: {self.title}, artists: {self.artists[0]}, album: {self.albums[0]}'


def process_yamusic_playlist(headers, user_id, playlist_id=YA_PLAYLIST_OF_THE_DAY_PATH):
    raw_response = requests.get(url=f'{YA_DOMAIN}/{YA_API_VERSION}/{playlist_id}/{user_id}', headers=headers)
    raw_response_json = raw_response.json()
    tracks_raw = raw_response_json['tracks']
    tracks_pretty = []
    for track in tracks_raw:
        tracks_pretty.append(Track(track))

    return tracks_pretty


tracks = process_yamusic_playlist(headers=YA_HEADERS, user_id=USER_ID)


# for track in tracks:
#     print(track.to_spotify_search_format())

def get_track_details(track):
    res = requests.get(url=f'{SPOTIFY_API_DOMAIN}/{SPOTIFY_API_VERSION}/{SPOTIFY_API_SEARCH_PATH}?q={track}&type'
                           f'=track,artist&limit=20&offset=5',
                       headers=SPOTIFY_HEADERS)
    return res


def search_tracks(tracks):
    found_tracks = []
    for track in tracks:
        full_info = get_track_details(track).json()
        items = full_info.get('tracks').get('items', [])
        if not items:
            track_essential_data = {'id': 'null', 'external_url': 'null'}
        else:
            track_essential_data = {
                'id': items[0].get('id'),
                'external_url': items[0].get('external_urls').get('spotify')
            }

        found_tracks.append(track_essential_data)
        # track = track.to_spotify_search_format()
    return found_tracks

def create_uris(tracks):
    uris = []
    for track in tracks:
        if track.get('id') and track.get('id') != 'null':
            uris.append(f'spotify:track:{track["id"]}')
    return ','.join(uris)
def post_to_playlist(uris):

    res = requests.post(url=f'{SPOTIFY_API_DOMAIN}/{SPOTIFY_API_VERSION}/playlists/{SPOTIFY_PLAYLIST_ID}/tracks?{uris}',
                       headers=SPOTIFY_HEADERS)

    return res.json()


test_tracks = [
    'track:Babooshka artist:Kate Bush',
    'track:Carnival of Rust artist:Poets Of The Fall', 'track:Космос artist:Три дня дождя']


found_tracks = search_tracks(test_tracks)
uris = create_uris(found_tracks)
print(uris)
res = post_to_playlist(uris)

print(res)
