# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 22:47:41 2015

@author: lpbrown999 / /u/oiturtlez
"""

import http.client as httplib
import os
import httplib2
import random
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow, argparser

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_UPLOAD_SCOPE = 'https://www.googleapis.com/auth/youtube.upload'
CLIENT_SECRETS_FILE = 'client_secret.json'

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

httplib2.RETRIES = 1
MAX_RETRIES = 10
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   {}

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""".format(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE)))


def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE, message=MISSING_CLIENT_SECRETS_MESSAGE)
    storage = Storage("storage.json")
    credentials = storage.get()
    args = argparser.parse_args()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return(build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http())))

def initialize_upload(youtube, file, video_title, video_description, tags_list, categoryId):  #authenticated youtube service, file name as string, video title as string, video description as string, tags as list, category numeric id as string
    body=dict(
        snippet=dict(
            title=video_title,
            description= video_description,
            tags=tags_list,
            categoryId=categoryId
        ),
        status=dict(
            privacyStatus="public"
        )
    )
    
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file, chunksize=-1, resumable=True))
    return(resumable_upload(insert_request))

def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading File")
            status, response = insert_request.next_chunk()
            if 'id' in response:
                print("Video id {} was successfully uploaded.".format(response['id']))
                return(response)
            else:
                exit("The upload failed with an unexpected response: {}".format(response))
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error {} occurred:\n {}".format(e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: {}".format(e)
        
        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")
        
            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping {} seconds and then retrying...".format(sleep_seconds))
            time.sleep(sleep_seconds)


def upload(file, video_title, video_description, tags_list, categoryId):
    youtube = get_authenticated_service()
    try:  
        a = initialize_upload(youtube, file, video_title, video_description, tags_list, categoryId)
        print(a['id'])
        return(a['id'])
    except HttpError as e:
        print("An HTTP error occured {}".format(e))
        
class setup_help(object):
    def __init__(self):
        print("helping!")
        print("For more help, try setup_help.google_project() setup_help.oauth(), setup_help.upload(), setup_help.categoryId()")
    def google_project(self):
        print("In order to use this module you must register a project with google as it uses their API.")
        print("To do so, travel to https://console.developers.google.com")
        print("From there, click on enable and manage API's and create a project. Then navigate to the API page.")
        print("At the API page, enable all of the YoutTube API's. Then navigate to the credentials page.")
        print("Create new OAuth client ID credentials. To do this you must follow a link to configure a consent screen, which is up to your discretion on what needs to be there.")        
        print("Ensure the application type selected for your project is 'other'")
        print("Then download the json file containing these credentials to the directory in which you will be running this module. Name this file client_secret.json")
        print("To determine category Ids, which are region specific, you must create an API browser key. More details on this can be found in setup_help.categoryId()")
    def oauth(self):
        print("You will need to place your client_secret.json in the same directory that you are attempting to upload from")
        print("This can be downloaded from your project in the google developer console")
        print("More information can be found in setup_help.google_project()")
    def upload(self):
        print("The upload function is the main reason for this package.")
        print("To use it, you must have a registered google developers project and a populated client_secret.json in the same folder as this file.")
        print("If you have not yet uploaded a file from this directory, you will be prompted to specify which google account you would like to use. This will then populate a storage.json file")
        print("The file, video_title, video_description, and categoryId arguments of the upload fucntion should all be strings. 'Tags' should be a list of tags for the video.")
        print("For more help with the categoryId, try setup_help.categoryId()")
    def categoryId(self):
        print("Category Ids are numbers given as strings which classify the type of video.")
        print("They are region specific and therefore cannot be simply listed here")
        print("In order to obtain a list of category Ids for your account, you need to first create an API browser key for your google project")
        print("With this browser key, navigate to https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode={two-character-region}&key={YOUR_API_KEY} ")
        