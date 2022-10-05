#!/home/pi/Projects/py-drive/tvenv/bin/python
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import logging
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s',
                                    datefmt='%m/%d/%Y %I:%M:%S %p')
logFile = 'run.log'

#logging.basicConfig(filename='run.log', encoding='utf-8',\
#                     level=logging.DEBUG, \
#                     format='%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p' \
#                    )
# https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=1*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.DEBUG)

app_log.addHandler(my_handler)



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

# Cron entry after sheband and execution bit set 
# 0 * * * * /home/pi/Projects/py-drive/readdrive2.py >> /home/pi/Projects/py-drive/drive-run.log 2>&1
# cat /var/log/syslog

from datetime import datetime
import glob
import os
import io

import shutil

# Source 
# https://developers.google.com/drive/api/quickstart/python
# https://dev.to/ajeebkp23/google-drive-api-access-via-service-account-python-33le
# https://www.thepythoncode.com/article/using-google-drive--api-in-python
import sqlite3
    


def downloadfile(drive_service,file_id,new_name):
    nasppath = r"/media/pidrive/nas-1tb/pyuploads/"
    tdate = datetime.today().strftime('%Y-%m-%d')

    naspath = nasppath + tdate + '/'
    # Check whether the specified path exists or not
    if not os.path.exists(naspath):
        # Create a new directory because it does not exist
        os.makedirs(naspath)
        app_log.debug("The new directory is created!")

    app_log.debug(f'Into download function for {new_name}')
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
        dst_path = naspath + new_name
        shutil.copy(src_path, dst_path)
        print('Copied')
        os.remove(new_file)
        app_log.info(f'Completed download and move for {new_name}')
    return (naspath,new_name)

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    connection_obj = sqlite3.connect('files.db')
    # cursor object
    cursor_obj = connection_obj.cursor()
    insertsql = """ INSERT INTO FILENAMES (File_name, File_path)
                VALUES(?,?)  
                """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        app_log.warning('No creds or expired')
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        app_log.info('token generated')

 
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
            app_log.info('No Files found')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
            fpath,fname  = downloadfile(service,item['id'],item['name'])
 
            cursor_obj.execute(insertsql,(fpath,fname))
 
            service.files().delete(fileId=item['id']).execute()
            app_log.info(f"Deleted {item['name']} from drive")
        app_log.info(f'Completed Page Size of {pageSize}')
        # Close the connection
        connection_obj.commit()
        connection_obj.close()


    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        app_log.error('Error occured')


if __name__ == '__main__':
    main()