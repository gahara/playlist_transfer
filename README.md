# Replicate playlists
## Yandex.Music -> Spotify
### How it works:
 - get songs' info from yamusic
 - use search by text in spotify
 - create playlist with songs spotify was able to find

To get permissions for the app to interact with user data, you need to run nodejs server from https://developer.spotify.com/documentation/web-api/quick-start/ one time to get access to data from browser. Or you can implement your own.

Replace credentials, add more to scope: playlist-modify-public playlist-modify-private
