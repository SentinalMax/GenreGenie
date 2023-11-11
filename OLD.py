import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from tqdm import tqdm
from colorama import Fore

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
                                               scope="user-library-read user-library-modify playlist-modify-private",
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
    

genres_to_filter = ['rock', 
                    'funk rock', 
                    'metal', 
                    'funk metal', 
                    'post-grunge', 
                    'alternative rock', 
                    'nu metal', 
                    'classic rock', 
                    'glam metal', 
                    'hard rock', 
                    'album rock', 
                    'pop rock']

# Start Program
def main():
    
    # Variables
    pages = 30 # each page yields 20 results (max=20)
    offset = 0
    track_cnt = 0
    
    user_info = sp.current_user()
    user_id = user_info.get('id', '')
    #print(user_id) #DEBUG
    new_plist = create_playlist(name="Metal", 
                                public=False, 
                                colab=False,
                                desc="All Metal/Rock Music from Liked Songs",
                                user=user_id)
    plist_id = new_plist.get('id', '')
    #print(plist_id) #DEBUG
    # print(new_plist) #DEBUG
    
    # Initialize tqdm progress bar for pages
    for page in tqdm(range(pages), 
                     desc="Processing pages",
                     colour="blue",
                     unit="page"):

        plist_data = sp.current_user_saved_tracks(limit=20, offset=offset)
        #print(plist_data) #DEBUG
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


