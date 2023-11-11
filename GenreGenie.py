import argparse
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from tqdm import tqdm
from colorama import Fore

# Initialize the parser
parser = argparse.ArgumentParser(description='Create a Spotify playlist based on given criteria.')

# Adding arguments
parser.add_argument('genres', type=str, help='List of genres to filter, separated by commas.')
parser.add_argument('--name', type=str, required=True, help='Name of the playlist.')
parser.add_argument('--public', type=bool, required=False, default=False, help='Whether the playlist should be public or not.')
parser.add_argument('--desc', type=str, required=True, help='Description of the playlist.')
parser.add_argument('--collab', type=bool, required=False, default=False, help='Whether the playlist should be collaborative.')
parser.add_argument('--pages', type=int, required=False, default=20, help='Pages to iterate through, each page yields 20 tracks; defaults to 20 (iterates through 400 songs), you may need to adjust this value depending on how many liked songs you have.')

# Parse arguments
args = parser.parse_args()

# The genres_to_filter will now be a list of genres input by the user, split by commas.
genres_to_filter = args.genres.split(',')

# Use the other arguments as needed in your script
playlist_name = args.name
playlist_public = args.public
playlist_desc = args.desc
playlist_collab = args.collab
playlist_pages = args.pages

# Get client data
json_file_path = 'client_keys.json'

with open(json_file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()
    #print(file_content) #DEBUG

    data = json.loads(file_content)
    client_info = data[0]

# Access the first item's values directly
client_id = client_info.get('id', '')
client_secret = client_info.get('secret', '')

# Init spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://localhost:3000",
                                               scope="user-library-read user-library-modify playlist-modify-private, playlist-modify-public",
                                               requests_timeout=10
                                               ))

# Functions

def format_json(json_object):
    formatted_json = json.dumps(json_object, indent=4)
    return formatted_json

def get_song_genre(track_identifier):
        
    # Step 1: Use the track's ID to get the track's artist(s)
    track_details = sp.track(track_id=track_identifier)
    #print(track_details) #DEBUG
    artist_ids = [artist['id'] for artist in track_details['artists']]
        
    # Step 2: Retrieve genres for each artist
    genres = set()
    for artist_id in artist_ids:
        artist_info = sp.artist(artist_id)
        genres.update(artist_info['genres'])
        
    return genres

def create_playlist(name, public, colab, desc, user):
    playlist = sp.user_playlist_create(user=user, 
                                        name=name, 
                                        public=public, 
                                        collaborative=colab, 
                                        description=desc)
    return playlist

# Start Program
def main():
    
    # Variables
    pages = playlist_pages # each page yields 20 results (max=20)
    offset = 0
    track_cnt = 0
    
    user_info = sp.current_user()
    user_id = user_info.get('id', '')
    #print(user_id) #DEBUG
    new_plist = create_playlist(name=playlist_name, 
                                public=playlist_public, 
                                colab=playlist_collab,
                                desc=playlist_desc,
                                user=user_id)
    plist_id = new_plist.get('id', '')
    
    # Initialize tqdm progress bar for pages
    for page in tqdm(range(pages), 
                     desc="Processing pages",
                     colour="blue",
                     unit="page"):

        plist_data = sp.current_user_saved_tracks(limit=20, offset=offset)
        tracks = plist_data.get('items', {})
        
        # Initialize tqdm progress bar for tracks within the current page
        for track in tqdm(tracks, 
                          desc=f"Page {page+1}/{pages}",
                          colour="green",
                          unit="track"):
            
            song = track.get('track', '')
            song_id = song.get('id', '')
            song_name = song.get('name', '')
            genres = get_song_genre(song_id)
            
            if any(genre in genres_to_filter for genre in genres):
                #print(f"Name: {song_name}") #DEBUG
                sp.user_playlist_add_tracks(user=user_id, playlist_id=plist_id, tracks=[song_id])  # Make sure to pass a list of song_ids
                track_cnt+=1 # update the track counter
                
        offset += 20 # update offset
    print(f"{Fore.BLUE}Tracks Added:{Fore.WHITE} {track_cnt}")
                
if __name__ == "__main__":
  main()


