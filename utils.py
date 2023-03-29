import requests
from dotenv import dotenv_values
import base64
import typing
from typing_extensions import TypedDict

secret_conf = dotenv_values('.env')

# region constants
YA_DOMAIN = 'https://music.yandex.ru/api'
YA_API_VERSION = 'v2.1'
YA_PLAYLIST_OF_THE_DAY_PATH = 'handlers/playlist/<username>'
USER_ID = secret_conf['Ya-music-id']
YA_HEADERS = {
    'Accept': 'application/json; q=1.0, text/*; q=0.8, */*; q=0.1',
    'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8,ja;q=0.7',
    # 'Connection': 'keep-alive'
    'X-Current-UID': secret_conf['X-Current-UID'],
    'Cookie': secret_conf['Cookie'],
    'X-Retpath-Y': 'https%3A%2F%2Fmusic.yandex.ru%2Fhome'
}

SPOTIFY_API_DOMAIN = 'https://api.spotify.com'
SPOTIFY_API_VERSION = 'v1'
SPOTIFY_API_SEARCH_PATH = 'search'
SPOTIFY_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': secret_conf['Spotify-Bearer']
}
SPOTIFY_PLAYLIST_ID = secret_conf['Spotify-playlist-id']
SPOTIFY_APP_CLIENT_ID = secret_conf['Client_id']
SPOTIFY_APP_CLIENT_SECRET = secret_conf['Client_secret']
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_REFRESH_TOKEN = secret_conf['Spotify-refresh-token']

# region Types
SpotifyURI = str


class YaArtist(TypedDict):
    name: str


class YaAlbum(TypedDict):
    title: str


class YaTrack(TypedDict):
    title: str
    artists: typing.List[YaArtist]
    albums: typing.List[YaAlbum]


# endregion

class Track:
    pass


class Album:
    def __init__(self, album_info: typing.Dict[str, str]):
        self.title: str = album_info.get('title')

    def __str__(self):
        return self.title


class Artist:
    def __init__(self, artist_info: YaArtist):
        self.name: str = artist_info.get('name')

    def __str__(self):
        return self.name


class TrackYa:
    def __init__(self, track_info: YaTrack):
        self.title = track_info.get('title')
        self.artists = self.get_artists(self, track_info=track_info)
        self.albums = self.get_albums(self, track_info=track_info)

    @staticmethod
    def get_artists(self, track_info: YaTrack) -> typing.List[Artist]:
        artists: typing.List[Artist] = []
        for artist in track_info.get('artists'):
            artists.append(Artist(artist))
        return artists

    @staticmethod
    def get_albums(self, track_info: YaTrack) -> typing.List[Album]:
        albums: typing.List[Album] = []
        for album in track_info.get('albums'):
            albums.append(Album(album))
        return albums

    def to_spotify_search_format(self) -> str:
        return f'track:{self.title} artist:{self.artists[0].name}'

    def __str__(self):
        return f'name: {self.title}, artists: {self.artists[0]}, album: {self.albums[0]}'


class TrackSp(Track):
    def __init__(self, track_info):
        self.title: str = track_info.get('name')
        self.id: str = track_info.get('id', 'null')
        self.external_url: str = track_info.get('external_urls', {'spotify': 'null'}).get('spotify')

    def __str__(self):
        return f'name: {self.title}, id: {self.id}'


def process_yamusic_playlist(headers, user_id, playlist_id=YA_PLAYLIST_OF_THE_DAY_PATH):
    raw_response = requests.get(url=f'{YA_DOMAIN}/{YA_API_VERSION}/{playlist_id}/{user_id}', headers=headers)
    raw_response_json = raw_response.json()
    tracks_raw = raw_response_json['tracks']
    tracks_raw = list(filter(lambda x: (isinstance(x, dict)),tracks_raw))

    tracks_pretty = []
    for track in tracks_raw:
        tracks_pretty.append(TrackYa(track).to_spotify_search_format())

    return tracks_pretty


# TODO: add spotify track class description
def search_track_by_name(track: str):
    res = requests.get(url=f'{SPOTIFY_API_DOMAIN}/{SPOTIFY_API_VERSION}/{SPOTIFY_API_SEARCH_PATH}?q={track}&type'
                           f'=track,artist&limit=20',
                       headers=SPOTIFY_HEADERS)
    return res


def search_tracks(tracks: typing.List[str]):
    found_tracks = []
    for track in tracks:
        full_info = search_track_by_name(track).json()
        items = full_info.get('tracks').get('items', [])
        if not items:
            track_essential_data = TrackSp({'id': 'null'})
        else:
            track_essential_data = TrackSp(items[0])

        found_tracks.append(track_essential_data)
    return found_tracks


def create_uris(tracks: typing.List[TrackSp]) -> SpotifyURI:
    uris: typing.List[SpotifyURI] = []
    for track in tracks:
        id = track.id
        if id and id != 'null':
            uris.append(f'spotify:track:{id}')
    return ','.join(uris)


def post_to_playlist(uris: SpotifyURI):
    res = requests.post(
        url=f'{SPOTIFY_API_DOMAIN}/{SPOTIFY_API_VERSION}/playlists/{SPOTIFY_PLAYLIST_ID}/tracks?uris={uris}',
        headers=SPOTIFY_HEADERS)

    return res.json()


# can't be used to update playlist/manipulate user data
def get_the_token():
    auth_client = f'{SPOTIFY_APP_CLIENT_ID}:{SPOTIFY_APP_CLIENT_SECRET}'
    auth_encode = 'Basic ' + base64.b64encode(auth_client.encode()).decode()
    headers = {
        'Authorization': auth_encode,
    }
    data = {
        'grant_type': 'client_credentials',
    }

    response = requests.post(SPOTIFY_AUTH_URL, data=data, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['access_token']
    else:
        print(f'ERROR: {response.json()})')


# can be used to update access token until expires
def refesh_the_token():
    auth_client = f'{SPOTIFY_APP_CLIENT_ID}:{SPOTIFY_APP_CLIENT_SECRET}'
    auth_encode = 'Basic ' + base64.b64encode(auth_client.encode()).decode()
    headers = {
        'Authorization': auth_encode,
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': SPOTIFY_REFRESH_TOKEN
    }

    response = requests.post(SPOTIFY_AUTH_URL, data=data, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['access_token']
    else:
        print(f'ERROR: {response.json()})')

# for big playlists
def divide_into_chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


spotify_access_token = get_the_token()

# refresh user access token
spotify_access_token = refesh_the_token()
# update headers
SPOTIFY_HEADERS['Authorization'] = f'Bearer {spotify_access_token}'
# get tracks form yamusic plalist
tracks = process_yamusic_playlist(headers=YA_HEADERS, user_id=USER_ID)
# search tracks by name and artist in spotify's library

found_tracks = search_tracks(tracks)
# transform tracks to format that spotify understands
uris = create_uris(found_tracks)

# split uris into chunks
uris_by_one = uris.split(',')
uris_in_chunks = list(divide_into_chunks(uris_by_one, 60))
chunk_for_playlist = [','.join(chunk) for chunk in uris_in_chunks]

print(chunk_for_playlist)
# post tracks
res = [post_to_playlist(uri) for uri in chunk_for_playlist]
print(res)




