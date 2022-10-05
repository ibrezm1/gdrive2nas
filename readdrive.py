import os.path

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


import glob
import os
import io



# Source 
# https://developers.google.com/drive/api/quickstart/python
# https://dev.to/ajeebkp23/google-drive-api-access-via-service-account-python-33le

def downloadfile(drive_service,file_id,new_name):
    request = drive_service.files().get_media(fileId=file_id)
    #fh = io.BytesIO() # this can be used to keep in memory
    fh = io.FileIO(new_name, 'wb') # this can be used to write to disk
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))



def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    list_of_files = glob.glob('s*.json') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)

    creds = Credentials.from_service_account_file(latest_file)



    try:
        service = build('drive', 'v3', credentials=creds)



        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        # Reading only files inside the folder 
        id = '11SAYpiK2H4ydZTZs60XNdfCS4AomGwgx'
        results = service.files().list(q = "'" + id + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
            downloadfile(service,item['id'],item['name'])
            #service.files().delete(fileId=item['id']).execute()

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')




if __name__ == '__main__':
    main()