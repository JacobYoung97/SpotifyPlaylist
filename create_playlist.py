import json
import requests
import os
import youtube_dl
from exceptions import ResponseException

from secrets import spotify_user_id, spotify_token
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

class CreatePlaylist:

    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}
        self.playlists = {}
    
    # Step 1: Log into youtube
    def get_youtube_client(self):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, 
                scopes
            )
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
                api_service_name, 
                api_version, 
                credentials = credentials
            )

        return youtube_client
    
    # Step 1.5: Get the list of all the playlists the user has made (liked videos is hardcoded as choice 1)
    def get_playlists(self):
        playlists = {}
        num = 2
        request = self.youtube_client.playlists().list(
            part = "snippet,contentDetails",
            maxResults = 50,
            mine = True
        )
        response = request.execute()

        for item in response["items"]:
            print(str(num) + ". " + item["snippet"]["title"])
            self.playlists[num] = item["id"]
            num += 1

    # Step 2: Grab our liked videos & create a dictionary of important song information
    def get_liked_videos(self):
        # TODO: find a way to iterate through an entire playlist of videos
        request = self.youtube_client.videos().list(
            part = "snippet,contentDetails,statistics",
            maxResults = 50,
            myRating = "like"
        )
        response = request.execute()

        # collect each video and get important information
        # TODO: find a way to get more pages of videos from the playlist
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["id"])

            # use youtube_dl to collect the song name & artist name
            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download = False)
            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None and artist is not None:
                # save all important information
                self.all_song_info[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,

                    # add the uri, easy to get song to put into playlist
                    "spotify_uri": self.get_spotify_url(song_name, artist)
                }
    
    # Step 2: Grab the videos from the playlist & create a dictionary of important song information
    # The only difference between this one and the get_liked_videos one is the location of the video id
    def get_playlist_videos(self, playlist):
        # playlistId is the one saved in the dictionary from earlier
        request = self.youtube_client.playlistItems().list(
            part = "snippet,contentDetails",
            maxResults = 50,
            playlistId = self.playlists[playlist]
        )
        response = request.execute()

        # TODO: find a way to get more pages of videos from the playlist
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["contentDetails"]["videoId"])

            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download = False)
            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None and artist is not None:
                # save all important information
                self.all_song_info[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,

                    # add the uri, easy to get song to put into playlist
                    "spotify_uri": self.get_spotify_url(song_name, artist)
                }

    # Step 3: Create A New Playlist
    def create_playlist(self):
        print("\nEnter the playlist name: ", end = "")
        playlistName = input()

        print("\nEnter a description: ", end = "")
        description = input()

        print("\nIs it public? (y or n): ", end = "")
        public = input()

        if public.lower() == "y":
            public = True
        else:
            public = False

        request_body = json.dumps({
            "name": playlistName,
            "description": description,
            "public": public
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
    def get_spotify_url(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        
        # only use the first song (if the result doesn't return anything then this checks)
        if len(songs) != 0:
            uri = songs[0]["uri"]
        else:
            uri = ""
        
        return uri
    
    # Step 5: Add this song into the new Spotify playlist
    def add_song_to_playlist(self):
        # populate our songs dictionary
        # TODO: change this to ask which playlist they would like to gather videos from
        print("Select the playlist you would like to send to Spotify")
        self.playlists[1] = "Liked videos"
        print("1. Liked videos")
        self.get_playlists()
        print("Number: ", end = "")
        num = input()

        # If the choice is 1, then we get the liked videos; otherwise we get the videos from that playlist
        if int(num) == 1:
            self.get_liked_videos()
        else:
            self.get_playlist_videos(int(num))

        # collect all uris
        uris = []
        for song, info in self.all_song_info.items():
            uris.append(info["spotify_uri"])

        # create a new playlist
        playlist_id = self.create_playlist()

        # add all new songs into playlist
        request_data = json.dumps(uris)
        print(request_data)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

        response = requests.post(
            query,
            data = request_data,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )

        # check for valid response status   
        if response.status_code != 200 || response.status_code != 201:
            raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json

if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.add_song_to_playlist()