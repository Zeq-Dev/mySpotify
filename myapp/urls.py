from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("auth/", views.auth, name="auth"),
    path("track/", views.track, name="track"),
    path("callback/", views.callback, name="callback"),
    path("current_song_cover/", views.current_song_cover, name="current_song_cover"),
    path("sign_out/", views.sign_out, name="sign_out"),
    path("song_prog/", views.sp.song_prog, name="song_prog")
]