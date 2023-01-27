import requests
import json
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

available_genres = {"acoustic",
    "afrobeat",
    "alt-rock",
    "alternative",
    "ambient",
    "anime",
    "black-metal",
    "bluegrass",
    "blues",
    "bossanova",
    "brazil",
    "breakbeat",
    "cantopop",
    "chicago-house",
    "children",
    "chill",
    "classical",
    "club",
    "comedy",
    "country",
    "dance",
    "dancehall",
    "death-metal",
    "deep-house",
    "detroit-techno",
    "disco",
    "disney",
    "drum-and-bass",
    "dub",
    "dubstep",
    "edm",
    "electro",
    "electronic",
    "emo",
    "folk",
    "forro",
    "french",
    "funk",
    "garage",
    "german",
    "gospel",
    "goth",
    "grindcore",
    "groove",
    "grunge",
    "guitar",
    "happy",
    "hard-rock",
    "hardcore",
    "hardstyle",
    "heavy-metal",
    "hip-hop",
    "holidays",
    "honky-tonk",
    "house",
    "idm",
    "indian",
    "indie",
    "indie-pop",
    "industrial",
    "iranian",
    "j-dance",
    "j-idol",
    "j-pop",
    "j-rock",
    "jazz",
    "k-pop",
    "kids",
    "latin",
    "latino",
    "malay",
    "mandopop",
    "metal",
    "metal-misc",
    "metalcore",
    "minimal-techno",
    "movies",
    "mpb",
    "new-age",
    "new-release",
    "opera",
    "pagode",
    "party",
    "philippines-opm",
    "piano",
    "pop",
    "pop-film",
    "post-dubstep",
    "power-pop",
    "progressive-house",
    "psych-rock",
    "punk",
    "punk-rock",
    "r-n-b",
    "rainy-day",
    "reggae",
    "reggaeton",
    "road-trip",
    "rock",
    "rock-n-roll",
    "rockabilly",
    "romance",
    "sad",
    "salsa",
    "samba",
    "sertanejo",
    "show-tunes",
    "singer-songwriter",
    "ska",
    "sleep",
    "songwriter",
    "soul",
    "soundtracks",
    "spanish",
    "study",
    "summer",
    "swedish",
    "synth-pop",
    "tango",
    "techno",
    "trance",
    "trip-hop",
    "turkish",
    "work-out",
    "world-music"}

# application constants
AUTH_BASE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
REDIRECT_URI = 'https://open.spotify.com/collection/playlists'
#CLIENT_ID = ###
#CLIENT_SECRET = ###
BASE_URL = 'https://api.spotify.com/v1/'

def get_token():
    
    scope = [
        "playlist-modify-private",
        "playlist-modify-public"]
    
    spotify = OAuth2Session(CLIENT_ID, scope=scope, redirect_uri=REDIRECT_URI)
    
    # Redirect user to Spotify for authorization
    auth_url, state = spotify.authorization_url(AUTH_BASE_URL)
    print('Please go here and authorize: ', auth_url)
    
    # Get the authorization verifier code from the callback url
    redirect_response = input('\n\nPaste the full redirect URL here: ')
    
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    return spotify.fetch_token(TOKEN_URL, auth=auth, authorization_response=redirect_response)['access_token']


def get_track_info(_track, _artist, headers):
    
    r = requests.get(BASE_URL + 
                     f'search?q=artist:{_artist}%20track:{_track}%20&type=track', 
                     headers=headers)
    r = r.json() 
    track_name = r['tracks']['items'][0]['name']
    artist_name = r['tracks']['items'][0]['artists'][0]['name']
    track_id = r['tracks']['items'][0]['id']
    artist_id = r['tracks']['items'][0]['artists'][0]['id']
    return track_name, track_id, artist_name, artist_id


def get_genres(_artist_id, headers):
    
    r = requests.get(BASE_URL + 
                     f'artists/{_artist_id}',
                     headers = headers)
    r = r.json()
    genre_options = ' '.join(r['genres']).split(' ')
    genres = ''
    for i in genre_options: #looks like max 3 seed genres allowed, haven't accounted
        if i in available_genres:
            genres += i
            genres += ', '
    
    return genres[:-2] # doesnt account for no genres

def get_suggestions(_track_id, _artist_id, _genres, headers):
    r = requests.get(BASE_URL +
                     f'recommendations?limit=25&seed_artists={_artist_id}&seed_genres={_genres}&seed_tracks={_track_id}',
                     headers = headers)
    r = r.json()
    
    suggestion_track_uris = []
        
    for track in r['tracks']:
        suggestion_track_uris.append(track['uri'])
    return suggestion_track_uris

def create_playlist(_track_title, _suggestions, headers):
    
    user_id = 'charlielillywhite1998'
    
    playlist_data = json.dumps({
          "name": f"Songs like {_track_title}",
          "description": "Song suggestions generated by Python and the Spotify API!",
          "public": False 
        })
    
    make_playlist = requests.post(BASE_URL + f'users/{user_id}/playlists', 
                                  data = playlist_data, headers = headers)
    
    playlist_id = make_playlist.json()['id']
    
    songs = json.dumps({
          "uris" : _suggestions
       })
    
    add_songs = requests.post(BASE_URL + f'playlists/{playlist_id}/tracks', 
                              data = songs,
                              headers = headers)
    return add_songs.json()

def main():
    token = get_token()
    headers = {
            "Content-Type":"application/json",
            'Authorization': f'Bearer {token}'
            }
    
    track = input('Track Name: ')
    artist = input('Artist Name: ')
    
    print(f'building a playlist of songs like {track} by {artist}')
    
    track_name, track_id, artist_name, artist_id = get_track_info(track, artist, headers)
    
    genres = get_genres(artist_id, headers)
    
    
    suggestions = get_suggestions(track_id, artist_id, genres, headers)
    
    
    create_playlist(track_name, suggestions, headers)
    
    print('Finished! Head to SPotify to see your new playlist.')
    
if __name__=='__main__':
    main()
