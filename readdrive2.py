#!/home/pi/Projects/py-drive/tvenv/bin/python
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import logging
logging.basicConfig(filename='run.log', encoding='utf-8',\
                     level=logging.DEBUG, \
                     format='%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p' \
                    )
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

# Cron entry after sheband and execution bit set 
# 0 * * * * /home/pi/Projects/py-drive/readdrive2.py >> /home/pi/Projects/py-drive/drive-run.log 2>&1
# cat /var/log/syslog


import glob
import os
import io

import shutil

# Source 
# https://developers.google.com/drive/api/quickstart/python
# https://dev.to/ajeebkp23/google-drive-api-access-via-service-account-python-33le
# https://www.thepythoncode.com/article/using-google-drive--api-in-python


def downloadfile(drive_service,file_id,new_name):
    logging.debug(f'Into download function for {new_name}')
    request = drive_service.files().get_media(fileId=file_id)
    #fh = io.BytesIO() # this can be used to keep in memory
    new_file = 'data/' + new_name
    fh = io.FileIO(new_file, 'wb') # this can be used to write to disk
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    if done:
        src_path = new_file
        dst_path = r"/media/pidrive/nas-1tb/pyuploads/" + new_name
        shutil.copy(src_path, dst_path)
        print('Copied')
        os.remove(new_file)
        logging.info(f'Completed download and move for {new_name}')


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        logging.warning('No creds or expired')
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        logging.info('token generated')

 
    try:
        service = build('drive', 'v3', credentials=creds)

        #del_file_id = '1s_4baWRfaHEk0H9jILR9-8rj9JaReDKK'
        #service.files().delete(fileId=del_file_id).execute()

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        # Reading only files inside the folder 
        id = '11SAYpiK2H4ydZTZs60XNdfCS4AomGwgx'
        pageSize = 15
        results = service.files().list(q = "'" + id + "' in parents", pageSize=pageSize, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            logging.info('No Files found')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
            downloadfile(service,item['id'],item['name'])
            service.files().delete(fileId=item['id']).execute()
            logging.info(f"Deleted {item['name']} from drive")
        logging.info(f'Completed Page Size of {pageSize}')

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        logging.error('Error occured')


if __name__ == '__main__':
    main()