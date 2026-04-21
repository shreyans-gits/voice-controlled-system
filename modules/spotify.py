import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config

class SpotifyModule:
    def __init__(self):
        scope = "user-modify-playback-state user-read-playback-state"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config.SPOTIFY_ID,
            client_secret=config.SPOTIFY_SECRET,
            redirect_uri=config.SPOTIFY_URI,
            scope=scope
        ))
    
    def play(self,song_name):
        try:
            if " by " in song_name:
                # Split "My Time by Emiway Bantai" into ["My Time", "Emiway Bantai"]
                parts = song_name.split(" by ")
                track = parts[0].strip()
                artist = parts[1].strip()
                # Create a specific search query
                query = f"track:{track} artist:{artist}"
            else:
                query = song_name
            results = self.sp.search(q=query, type="track", limit=1)
            
            if results["tracks"]["items"]:
                uri = results["tracks"]["items"][0]["uri"]
                track_name = results["tracks"]["items"][0]["name"]
                artist_name = results["tracks"]["items"][0]["artists"][0]["name"]
                
                self.sp.start_playback(uris=[uri])
                return f"Playing {track_name} by {artist_name}"
            else:
                return f"I couldn't find {song_name} on Spotify."
        except Exception as e:
            return f"Make sure Spotify is open! Error: {e}"
        
    def pause(self):
        try:
            self.sp.pause_playback()
            return "Paused"
        except Exception:
            return "Could not pause. Is music playing?"
        
    def next_track(self):
        try:
            self.sp.next_track()
            return "Skipped"
        except Exception:
            return "Could not skip track."
        