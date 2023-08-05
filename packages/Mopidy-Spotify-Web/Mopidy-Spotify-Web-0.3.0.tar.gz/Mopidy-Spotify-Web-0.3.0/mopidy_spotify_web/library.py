from __future__ import unicode_literals

import logging

import time
# no monotonic python 2
if not hasattr(time, 'monotonic'):
    time.monotonic = time.time

from mopidy import backend
from mopidy.models import Ref

import requests

import spotipy

from translator import to_mopidy_track
from translator import to_sauce_uri

logger = logging.getLogger(__name__)


def get_tracks_from_web_api(sp):
    return get_from_sp(sp, get_next_spotify_tracks_items,
                       spotify_get_tracks_process_results)


def spotify_get_tracks_process_results(results):
    logger.debug('Processing spotify get tracks result')
    tracks = [to_mopidy_track(item['track'])
              for item in results['items']]
    cont = results['next'] is not None
    logger.debug('Spotify get tracks result cont: %s' % cont)
    return tracks, cont


def get_next_spotify_tracks_items(sp, uri, limit, offset):
    logger.debug('Going to get spotify tracks,'
                 ' with limit %s with offset %s'
                 % (str(limit), str(offset)))

    return sp.current_user_saved_tracks(limit=limit, offset=offset)


def get_top_tracks_from_web_api(sp, uri):
    if sp is None:
        return []
    try:
        results = sp.artist_top_tracks(get_artist_from_uri(uri))
        logger.debug('Processing spotify top get tracks result')
        arr = [Ref.track(uri=track['uri'], name=track['name'])
               for track in results['tracks']]
    except spotipy.SpotifyException as e:
        logger.error('Spotipy error(%s): %s', e.code, e.msg)

    return arr


def get_albums_from_web_api(sp, uri):
    arr = [Ref.directory(
           uri='spotifyweb:sauce:artist-toptracks:%s'
           % get_artist_from_uri(uri),
           name='Top Tracks')]
    arr += get_from_sp(sp, get_albums_items,
                       spotify_albums_results, uri)
    return arr


def get_albums_items(sp, uri, limit, offset):
    logger.debug('Going to get albums,'
                 ' with limit %s with offset %s'
                 % (str(limit), str(offset)))

    return sp.artist_albums(get_artist_from_uri(uri),
                            limit=limit, offset=offset)


def get_artist_from_uri(uri):
    ids = uri.split(':')
    return ids[3]


def spotify_albums_results(results):
    logger.debug('Processing spotify albums result')
    albums = [Ref.album(uri=album['uri'],
                        name=album['name'])
              for album in results['items']]
    logger.debug('Processing spotify albums result; next %s' % results['next'])
    cont = results['next'] is not None
    logger.debug('Spotify get albums result cont: %s' % cont)
    return albums, cont


def get_fresh_token(config):
    try:
        logger.debug("authenticating")
        if config['use_mopidy_oauth_bridge']:
            response = get_fresh_token_from_mopidy(config)
        else:
            response = get_fresh_token_from_spotify(config)
        logger.debug("authentication response: %s", response.content)
        token_response = response.json()
        return token_response
    except requests.exceptions.RequestException as e:
        logger.error('Refreshing the auth token failed: %s', e)
    except ValueError as e:
        logger.error('Decoding the JSON auth token response failed: %s', e)


def get_fresh_token_from_mopidy(config):
    mopidy_token_url = config['mopidy_token_url']
    logger.debug("authentication using mopidy swap service on: %s",
                 mopidy_token_url)
    auth = (config['client_id'], config['client_secret'])
    return requests.post(mopidy_token_url, auth=auth, data={
        'grant_type': 'client_credentials',
    })


def get_fresh_token_from_spotify(config):
    spotify_token_url = config['spotify_token_url']
    logger.debug("authentication using spotify on: %s", spotify_token_url)
    auth = (config['client_id'], config['client_secret'])
    return requests.post(spotify_token_url, auth=auth, data={
        'grant_type': 'refresh_token',
        'refresh_token': config['refresh_token'],
    })


def get_from_sp(sp, get_next_items, process_results, uri=None):
    if sp is None:
        return []
    try:
        arr = get_from_sp_while_next(sp, get_next_items, process_results, uri)
    except spotipy.SpotifyException as e:
        logger.error('Spotipy error(%s): %s', e.code, e.msg)

    return arr


def get_from_sp_while_next(sp, get_next_items, process_results,
                           uri=None, arr=None, limit=50, offset=0):
    results = get_next_items(sp, uri, limit, offset)
    new_arr, cont = process_results(results)
    if arr is None:
        arr = []
    arr += new_arr
    if cont:
        new_offset = len(arr)
        return get_from_sp_while_next(sp, get_next_items,
                                      process_results, uri,
                                      arr, limit, new_offset)
    else:
        return arr


def spotify_browse_process_results(results):
    logger.debug('Processing spotify browse result')
    if 'categories' in results:
        result_list = results['categories']
        browse_uri = 'spotifyweb:browse:categories:'
        arr = [Ref.directory(uri=browse_uri + cat['id'],
                             name=cat['name'])
               for cat in result_list['items']]
    elif 'playlists' in results:
        result_list = results['playlists']
        arr = [Ref.playlist(uri=playlist['uri'],
                            name=playlist['name'])
               for playlist in result_list['items']]
    elif 'albums' in results:
        result_list = results['albums']
        arr = [Ref.album(uri=album['uri'],
                         name=album['name'])
               for album in result_list['items']]
    else:
        result_list = None
        arr = []

    cont = result_list is not None and result_list['next'] is not None
    logger.debug('Spotify browse result cont: %s' % cont)
    return arr, cont


def get_next_spotify_browse_items(sp, uri, limit, offset):
    ids = uri.split(':')
    webapi_url = '/'.join(ids[1:])

    # we browse the /playlists endpoint for categories
    if len(ids) == 4 and ids[2] == 'categories':
        webapi_url += '/playlists'

    logger.debug('Going to get spotify browse on url: %s,'
                 ' with limit %s with offset %s'
                 % (webapi_url, str(limit), str(offset)))

    return sp._get(webapi_url, limit=limit, offset=offset)


def get_spotify_browse_results(sp, uri):
    return get_from_sp(sp, get_next_spotify_browse_items,
                       spotify_browse_process_results, uri)


def token_is_fresh(sp, access_token_expires):
    return sp is not None and time.monotonic() < access_token_expires - 60


class SpotifyWebLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri='spotifyweb:directory',
                                   name='Spotify Web Browse')

    def __init__(self, *args, **kwargs):
        super(SpotifyWebLibraryProvider, self).__init__(*args, **kwargs)

        self._your_music = \
            [Ref.directory(uri='spotifyweb:yourmusic:songs', name='Songs'),
             Ref.directory(uri='spotifyweb:yourmusic:albums', name='Albums'),
             Ref.directory(uri='spotifyweb:yourmusic:artists', name='Artists')]
        self._browse = \
            [Ref.directory(uri='spotifyweb:browse:new-releases',
                           name='New Releases'),
             Ref.directory(uri='spotifyweb:browse:categories',
                           name='Genres & Moods'),
             Ref.directory(uri='spotifyweb:browse:featured-playlists',
                           name='Featured Playlists')]
        self._root = \
            [Ref.directory(uri='spotifyweb:yourmusic', name='Your Music'),
             Ref.directory(uri='spotifyweb:browse', name='Browse'),
             Ref.directory(uri='spotifyweb:sauce', name='Your Artists')]
        self._sp = None
        self._cache = None
        self._access_token = None
        self._access_token_expires = None

    def refresh(self, uri=None):
        sp = self.get_sp_webapi()
        if sp is not None:
            logger.debug('Loading spotify-web library from '
                         'web-api using token: %s', self._access_token)
            tracks = get_tracks_from_web_api(sp)
        else:
            logger.warn('Could not initialize spotipy web api instance')
            tracks = []
        self._cache = Cache(tracks)

    def get_sp_webapi(self):
        if token_is_fresh(self._sp, self._access_token_expires):
            return self._sp

        token_res = get_fresh_token(self.backend.config)
        if token_res is None or 'access_token' not in token_res:
            logger.warn('Did not receive authentication token!')
            return None

        self._access_token = token_res['access_token']
        self._access_token_expires = time.monotonic() + token_res['expires_in']
        self._sp = spotipy.Spotify(auth=self._access_token)
        return self._sp

    def lookup(self, uri):
        pass

    def browse(self, uri):
        logger.debug("Request to browse %s in SpotifyWebLibraryProvider", uri)
        if uri == self.root_directory.uri:
            return self._root
        elif uri.startswith('spotifyweb:yourmusic'):
            return self.browse_your_music(uri)
        elif uri.startswith('spotifyweb:browse'):
            return self.browse_browse(uri)
        elif uri.startswith('spotifyweb:sauce'):
            return self.browse_sauce(uri)
        else:
            return []

    def browse_browse(self, uri):
        if uri == 'spotifyweb:browse':
            return self._browse
        else:
            return get_spotify_browse_results(self._sp, uri)

    def browse_sauce(self, uri):
        if uri == 'spotifyweb:sauce':
            return [Ref.directory(uri=to_sauce_uri(artist.uri),
                                  name=artist.name)
                    for artist in self._cache.sortedArtists]
        elif uri.startswith('spotifyweb:sauce:artist-toptracks'):
            return get_top_tracks_from_web_api(self.get_sp_webapi(), uri)
        elif uri.startswith('spotifyweb:sauce:artist'):
            return get_albums_from_web_api(self.get_sp_webapi(), uri)
        else:
            return []

    def browse_your_music(self, uri):
        if uri == 'spotifyweb:yourmusic':
            return self._your_music
        if uri == 'spotifyweb:yourmusic:artists':
            return self._cache.sortedArtists
            # return Ref directory with all artists
        elif uri == 'spotifyweb:yourmusic:albums':
            return self._cache.sortedAlbums
            # return Ref directory for all albums
        elif uri.startswith('spotifyweb:yourmusic:artist:'):
            # get artist uri
            return self._cache.artists2albums.get(uri)
            # return Ref directory with all albums for artist
        elif uri.startswith('spotifyweb:yourmusic:album:'):
            # get album uri
            return self._cache.albums2tracks.get(uri)
            # return Ref directory with all tracks for album
        elif uri == 'spotifyweb:yourmusic:songs':
            return self._cache.tracks
        else:
            return []


class Cache:
    def __init__(self, tracks, *args, **kwargs):
        logger.debug("initializing SpotifyWebLibraryProvider cache")
        self.albums2tracks = {}
        self.artists2albums = {}
        self.sortedAlbums = []
        self.sortedArtists = []
        self.tracks = []
        self.trackDict = {}
        for t in tracks:
            logger.debug("Adding track %s", t.name)
            self.tracks.append(Ref.track(name=t.name, uri=t.uri))
            self.trackDict[t.uri] = t
            if hasattr(t, 'album'):
                self.add_album_and_artists(t)

        logger.debug('Sorting albums and artists')
        cmp_dir_names = lambda x, y: cmp(x.name, y.name)
        self.sortedAlbums.sort(cmp_dir_names)
        self.sortedArtists.sort(cmp_dir_names)
        logger.debug('Sorting albums by track number')
        for key in self.albums2tracks:
            logger.debug('Sorting album %s', key)
            album = self.albums2tracks[key]
            cmp_tracknos = lambda x, y: \
                cmp(self.trackDict[x.uri].track_no,
                    self.trackDict[y.uri].track_no)
            album.sort(cmp_tracknos)

    def add_album_and_artists(self, track):
        album = track.album

        name = album.name
        logger.debug('Going to add album %s', name)
        album_dir = Ref.directory(uri=album.uri, name=name)
        track_ref = Ref.track(name=track.name, uri=track.uri)
        if album.uri not in self.albums2tracks:
            self.sortedAlbums.append(album_dir)

        # adding track to album2tracks
        if album.uri in self.albums2tracks:
            if track_ref not in self.albums2tracks[album.uri]:
                self.albums2tracks[album.uri].append(track_ref)
        else:
            self.albums2tracks[album.uri] = [track_ref]

        if hasattr(track, 'artists'):
            self.add_artists(track, album_dir)

    def add_artists(self, track, album_dir):
        for artist in track.artists:
            artist_name = artist.name
            logger.debug('Going to add artist %s', artist_name)

            artist_dir = Ref.directory(uri=artist.uri, name=artist_name)
            if artist.uri not in self.artists2albums:
                self.sortedArtists.append(artist_dir)

            if artist.uri in self.artists2albums:
                if album_dir not in self.artists2albums[artist.uri]:
                    self.artists2albums[artist.uri].append(album_dir)
            else:
                self.artists2albums[artist.uri] = [album_dir]
