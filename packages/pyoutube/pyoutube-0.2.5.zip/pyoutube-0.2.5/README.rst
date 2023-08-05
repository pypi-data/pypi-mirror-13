pyoutube
--------
Requirements:

* Python 3.3 or higher

* Install the Google API's Client Library for python (https://developers.google.com/api-client-library/python/start/installation)

* A registered application with google (https://developers.google.com/youtube/registering_an_application)

* A populated client_secret.json file in the directory you will be uploading the file from.


Sample usage::

>>>from pyoutube import uploader
>>>uploader.upload("File.mp4", "Video Title", "Video Description", ["video", "tags"], "20")