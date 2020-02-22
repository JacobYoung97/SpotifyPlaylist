import json
import requests
from secrets import spotify_user_id, spotify_token

class CreatePlaylist:

    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
    
    # Step 1: Log Into Youtube
    def get_youtube_client(self):
        pass
    
    # Step 2: Grab Our Liked Videos
    def get_liked_videos(self):
        pass
    
    # Step 3: Create A New Playlist
    def create_playlist(self):
        request_body = json.dumps({
            "name": "Test Playlist"
            "description": "This is to test if a playlist can be created"
            "public": True
        })
        
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data = request_body,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()
        
        # The playlist's ID for later
        return response_json["id"]
    
    # Step 4: Search For the Song
    def get_spotify_url(self):
        pass
    
    # Step 5: Add this song into the new Spotify playlist
    def add_song_to_playlist(self):
        pass