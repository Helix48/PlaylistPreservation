from datetime import datetime, timedelta
import firebase_admin
import firebase_admin.credentials as credentials
import firebase_admin.db as db
import json
import logging
from Playlist import Playlist
from EmailResults import emailError

if not firebase_admin._apps:
    firebase_json = open("data.json")
    firebase_data = json.load(firebase_json)

    cred = credentials.Certificate(firebase_data["credentials"]) 

    try:
        default_app = firebase_admin.initialize_app(cred, {"databaseURL": firebase_data["databaseURL"]})
    except Exception as ex:
        error_msg = "Failed to connect to database"
        logging.exception(error_msg)
        emailError(error_msg, ex)

def postPlaylistsToFirebase(playlists_current):
    ref = db.reference("playlists", app = default_app)
    id = datetime.now().date()
    playlists_ref_current = ref.child(str(id))

    try:
        for playlist in playlists_current:
            playlists_ref_current.update({
                playlist.name : json.dumps(playlist.videos)
            })
    except Exception as ex:
        error_msg = "Failed to post data"
        logging.exception(error_msg)
        emailError(error_msg, ex)

def readPastPlaylistsFromFirebase():
    ref = db.reference("playlists", app = default_app)
    id = datetime.now().date() + timedelta(days=-1)
    playlists_ref_past = ref.child(str(id))

    playlists_past = []

    try:
        playlists_past_json = playlists_ref_past.get(etag=True)

        for playlist in playlists_past_json[0]:
            playlists_past.append(Playlist(playlist, "None", json.loads(playlists_past_json[0][playlist])))
    except Exception as ex:
        error_msg = "Failed to read data"
        logging.exception(error_msg)
        emailError(error_msg, ex)

    return playlists_past