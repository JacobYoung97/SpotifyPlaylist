# SpotifyPlaylist
Watching this video and basing the code off of her video:
https://www.youtube.com/watch?v=7J_qcttfnJA  
GitHub link to the original project idea: https://github.com/TheComeUpCode/SpotifyGeneratePlaylist

## My additions
While this may be based off of someone else's project, I plan on adding more to the basic application.

This would consist of:

* Checking all the user's playlists (the ones they have made)
* Going through EVERY video in liked videos or a specified YouTube playlist (defaults to the first 5 listed naturally)
* Adding the ability to give the Spotify playlist a name, description, and if it is public or not (original had default values)

## How to Use
Note, this assumes Python and Pip are already installed on your system

1.  Install dependencies
`pip install -r requirements.txt`

2. Collect the Spotify User ID and Auth Token and add it to a secrets.py file

3. Enable Ouath for YouTube and download client_secrets.json (if it has the token in the filename, remove it to have an easier to read name)

4. Run the file
`python create_playlist.py`