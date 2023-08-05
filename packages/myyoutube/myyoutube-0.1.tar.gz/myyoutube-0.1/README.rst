borrow from great pyoutube
--------
Requirements:

* Python 2.7 or higher

* Install the Google API's Client Library for python (https://developers.google.com/api-client-library/python/start/installation)

* A registered application with google (https://developers.google.com/youtube/registering_an_application)

* A populated client_secret.json file in the directory you will be uploading the file from.

To install::

>>> pip install myyoutube


Sample usage::

>>>from myyoutube import uploader
>>>uploader.upload("File.mp4", title="Video Title", description="Video Description", tags=["video", "tags"], categoryId="20",privacy_status="Public")

Returns a dictionary response containing information about the uploaded video.

This function is of the form uploader.upload(file,**kwargs).

Only the file parameter is required for the upload to occur, as all other parameters have defaults which will be used should the argument not be passed, however it is recommended to pass the arguments in order to upload an attractive youtube video.

List of optional arguments and their uses:

* title: string, becomes the title of the youtube video. 

* description: string, becomes the description of the youtube video.

* tags: list of strings, becomes the keyword tags of the youtube video.

* categoryId: string or an int, the numerical category id that categorizes the youtube video accordingly. These category ids can be obtained from the youtube web API via the link https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode={two-character-region}&key={YOUR_API_KEY}. You will need to enable a browser API key as part of your project to discover different categoryId's.

* privacy_status: string, must be one of "public", "unlisted", or "private". Defaults to "public".
