from flask import Flask, request, render_template, url_for
import os, json, requests, spotipy, pprint
import flaskapp.secret as secret
# import utils.(filename)
import dicttoxml

pp = pprint.PrettyPrinter()

app = Flask(__name__)

spot = None

positionData = {}

@app.route('/')
def show_page(): 
    return render_template("index.html") 

@app.route('/logged')
def show_another():
    global spot
    # get the auth portion of url
    code = request.args['code']
    print("spotify code", code)

    # make a post to spotify auth
    tokens = get_spotify_token(code)


    # get the spotify auth related tokens
    access_token = tokens['access_token']
    spot = spotipy.Spotify(auth=access_token)
    user = spot.me()
    username = user['id']

    # use location data to make the weather api call
    keywords = get_weather_keyword(42.3601, -71.0589)

    # use weather data to create a spotify playlist
    playlist = spot.user_playlist_create(username, 
        user['display_name']+"'s mood playlist", 
        public=False)

    playlist_id = playlist['id']

    pp.pprint(playlist)

    # tracks = []
    # spot.user_playlist_add_tracks(username, playlist_id)

    # store the id of the playlist. use the playlist id to play on speaker

    # requests.post
    return "Hello"

def get_spotify_token(code):
    url = "https://accounts.spotify.com/api/token"
    payload = {"grant_type": "authorization_code", "code": code, "redirect_uri":"http://localhost:5000/logged", 
        "client_id": secret.CLIENT, 
        "client_secret": secret.CLIENT_SECRET}
    res = requests.post(url, data=payload)
    resjson = res.json()
    print("RESPONSE FOR TOKEN REQUEST", resjson)
    return resjson

def get_weather_keyword(lat, lon):
    url = "https://api.darksky.net/forecast/f8e4346a41cff3c66e447fd9bc38c543/42.3601,-71.0589"
    res = requests.get(url)
    resData = res.json()
    keywords = {
      "timezone": resData['timezone'], # String
      "summary": resData['currently']['summary'], # String
      "cloudCover": resData['currently']['cloudCover'], # Float
      "windSpeed": resData['currently']['windSpeed'], # Float
      "temperature": resData['currently']['temperature'], # Float
      "precipIntensity": resData['currently']['precipIntensity'] # Float
    }
    print(keywords)
    return keywords

# -- Bose Speaker Info and Play playlist

def getBoseInfo(id):
    url = "http://192.168.1.157:8090/info"
    info = requests.get(url)
    print(info)

def playPlaylistOnBose(playlistId):
    url = "http://192.168.1.157:8090/select"
    payloadLeft = '<ContentItem source="SPOTIFY" type="uri" location="spotify:playlist:'
    payloadRight = '" sourceAccount="nav_suri" isPresetable="true"></ContentItem>'
    payload = payloadLeft + playlistId + payloadRight
    res = requests.post(url, data=payload)
    resJson = res.json()
    print(resJson)

# -- Navigation for Bose Speaker --

@app.route('/navigate/next', methods=['POST'])
def moveToNextTrack():
  url = "http://192.168.1.157:8090/key"
  payloadLeft = '<key state="press" sender="Gabbo">'
  payloadRight = '</key>'
  payload = payloadLeft + "PLAY_PAUSE" + payloadRight
  res = requests.post(url, data=payload)
  return ''

@app.route('/navigate/prev', methods=['POST'])
def moveToPrevTrack():
  url = "http://192.168.1.157:8090/key"
  payloadLeft = '<key state="press" sender="Gabbo">'
  payloadRight = '</key>'
  payload = payloadLeft + "PREV_TRACK" + payloadRight
  res = requests.post(url, data=payload)
  return ''

@app.route('/navigate/play', methods=['POST'])
def togglePlay():
  url = "http://192.168.1.157:8090/key"
  payloadLeft = '<key state="press" sender="Gabbo">'
  payloadRight = '</key>'
  payload = payloadLeft + "NEXT_TRACK" + payloadRight
  res = requests.post(url, data=payload)
  return ''