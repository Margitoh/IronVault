
import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveSyncManager:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.creds = None
        self.service = None
        self.credentials_file = credentials_file
        self.token_file = token_file

    def authenticate(self):
        """Authenticates the user using OAuth2 flow."""
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as token:
                    self.creds =  pickle.load(token) # Actually request uses pickle for some reason in many examples, but let's stick to standard if possible. 
                    # Google standard example uses pickle for token.json usually.
                    # Wait, recent libs might prefer json. load_credentials_from_file...
                    # Let's stick to the standard 'quickstart' pattern which is reliable.
                    pass
            except:
                pass

        # Re-do the standard pattern correctly
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    self.creds = None
            
            if not self.creds:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Missing {self.credentials_file}. You need to download it from Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)

        try:
            self.service = build('drive', 'v3', credentials=self.creds)
            return True, "Authenticated successfully."
        except Exception as e:
            return False, f"Failed to build service: {e}"

    def upload_file(self, file_path, file_name=None):
        """Uploads a file to Google Drive."""
        if not self.service:
            return False, "Not authenticated."

        if not file_name:
            file_name = os.path.basename(file_path)

        # Check if file already exists to update it instead of creating duplicate
        existing_file_id = self._get_file_id(file_name)

        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, resumable=True)

        try:
            if existing_file_id:
                # Update existing file
                file = self.service.files().update(
                    fileId=existing_file_id,
                    media_body=media).execute()
                return True, f"Updated file ID: {file.get('id')}"
            else:
                # Create new file
                # Ideally check / create a folder "IronVault Backups"
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id').execute()
                return True, f"Created file ID: {file.get('id')}"
        except Exception as e:
            return False, f"Upload failed: {e}"

    def list_backups(self):
        """Lists backup files in Drive."""
        if not self.service:
            return []
        
        try:
            results = self.service.files().list(
                q="name = 'vault.db' and trashed = false",
                pageSize=10, fields="nextPageToken, files(id, name, modifiedTime)").execute()
            items = results.get('files', [])
            return items
        except Exception as e:
            print(f"List failed: {e}")
            return []

    def download_file(self, file_id, destination_path):
        """Downloads a file from Drive."""
        if not self.service:
            return False, "Not authenticated."

        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            with open(destination_path, 'wb') as f:
                f.write(fh.getbuffer())
            return True, "Download complete."
        except Exception as e:
            return False, f"Download failed: {e}"

    def _get_file_id(self, filename):
        """Helper to check if a file exists."""
        items = self.list_backups() # This filters by vault.db specifically in list_backups q param
        # We might want to make list_backups more generic or this helper more specific
        # For now, let's just search specifically
        try:
            results = self.service.files().list(
                q=f"name = '{filename}' and trashed = false",
                pageSize=1, fields="files(id, name)").execute()
            files = results.get('files', [])
            if files:
                return files[0]['id']
        except:
            pass
        return None
