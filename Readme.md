## Simple gdrive to External HD tool 
This was created for moving files to nas mount, was fed up with open media server and other tools had to take over the task

## Installation steps 
* Refer the quick link [here](https://developers.google.com/drive/api/quickstart/python) for setup 
* Set up auth first time on local and move the token to raspberry once the autorization is done.
* readDrive earlier version uses service account to access, which as problems 
    * In can read files only those that are shared with the service account. 
    * It cannot delete from drive, due to permission issues ( Tried all could not get )
* drive can be set up as per [here](https://turbofuture.com/computers/Permanently-Mounting-a-USB-Harddrive-to-your-Raspberry-Pi)
* App has to be set up and the user id has to be explicitly entered to give access in [here](https://console.cloud.google.com/apis/credentials?project=zeta-yen-319702) for the OAuth2 clients 
* SCOPES are important if you want to read metadata only / file only / Delete files etc.
* Apart from the files mentioned, we would eventually need credential(from the google oauth/token(generated after first usage) or Serviceaccount(google IAM) json files for this to work correctly
* Refer [this](https://stackoverflow.com/questions/3287038/cron-and-virtualenv) for sheduling
* 4 * * * * cd /home/pi/Projects/py-drive && /home/pi/Projects/py-drive/readdrive2.py >> /home/pi/Projects/py-drive/drive-run.log 2>&1