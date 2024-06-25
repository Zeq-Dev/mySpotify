import time
from django.shortcuts import render, HttpResponse, redirect
import spotipy
import os
import json
from dotenv import load_dotenv
from django.http import JsonResponse

scope = "user-read-currently-playing"
sp = spotipy.Spotify()

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URL = os.getenv('SPOTIPY_REDIRECT_URI')

def home(request):
    if not request.session.get('token_info'):
        user_auth = 'Get Started'
        user_name = None
        state = 'none'
    else:
        user_auth = 'Open Track'
        user_name = sp.user_name(request)
        state = 'nav'

    return render(request, "home.html", {'user_auth': user_auth, 'user_name': user_name, 'state': state})

def auth(request):
    cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request)
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URL,
        scope=scope,
        cache_handler=cache_handler,
        show_dialog=True
    )
    
    if auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/track')

    auth_url = auth_manager.get_authorize_url()

    return redirect(auth_url)

def callback(request):
    cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request)
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URL,
        scope=scope,
        cache_handler=cache_handler,
        show_dialog=True
    )
    
    code = request.GET.get('code')
    token = auth_manager.get_access_token(code)

    request.session.modified = True
    auth_url = auth_manager.get_authorize_url()

    return redirect('/')

def sign_out(request):
    request.session.pop('token_info')
    return redirect('/')

def track(request):
    if request.session.get('token_info') is None:
        return redirect('/')
    song_cover = sp.song_cover(request)
    song_name = sp.song_name(request)
    song_artist = sp.song_artist(request)
    song_prog, ms = sp.song_prog(request)
    
    return render(request, 'track.html', {"song_cover": song_cover, 'song_name': song_name, 'song_artist': song_artist, 'song_prog': song_prog})

def current_song_cover(request):
    if not request.session.get('token_info'):
        return JsonResponse({"error": "User not authenticated"}, status=401)

    song_cover = sp.song_cover(request)
    song_name = sp.song_name(request)
    song_artist = sp.song_artist(request)
    song_prog, song_prog_ms = sp.song_prog(request)
    song_duration = sp.song_duration(request)
    
    return JsonResponse({
        "song_cover": song_cover,
        'song_name': song_name, 
        'song_artist': song_artist, 
        'song_prog': song_prog, 
        'song_prog_ms': song_prog_ms,
        'song_duration': song_duration
    })

class sp():
    def auth_data(request):
        cache_handler = spotipy.cache_handler.DjangoSessionCacheHandler(request)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        spotify = spotipy.Spotify(auth_manager=auth_manager)

        return spotify

    def user_name(request):
        spotify = sp.auth_data(request)

        user_name = spotify.me()['display_name']

        return user_name

    def song_cover(request):
        spotify = sp.auth_data(request)

        usernp_data = spotify.current_user_playing_track()
        if usernp_data and usernp_data.get('item'):
            song_cover = usernp_data['item']['album']['images'][0]['url']
            return song_cover
        return None
    
    def song_name(request):
        spotify = sp.auth_data(request)

        usernp_data = spotify.current_user_playing_track()
        if usernp_data and usernp_data.get('item'):
            song_name = usernp_data['item']['name']
            return song_name
        return None
    
    def song_artist(request):
        spotify = sp.auth_data(request)

        usernp_data = spotify.current_user_playing_track()
        if usernp_data and usernp_data.get('item'):
            song_artist = usernp_data['item']['artists']
            song_artists = []
            for artists in song_artist:
                song_artists.append(artists['name'])
            return song_artists
        return None

    def song_prog(request):
        spotify = sp.auth_data(request)

        usernp_data = spotify.current_user_playing_track()
        try:
            song_prog_ms = usernp_data['progress_ms']
        except:
            return None

        seconds = int((song_prog_ms/(1000))%60)
        minutes = int((song_prog_ms/(1000*60))%60)
        
        if len(str(seconds)) == 1:
            seconds = '0' + str(seconds)

        song_prog = f'{minutes}:{seconds}'

        return song_prog, song_prog_ms
    
    def song_duration(request):
        spotify = sp.auth_data(request)

        usernp_data = spotify.current_user_playing_track()
        duration = usernp_data['item']['duration_ms']

        return duration
