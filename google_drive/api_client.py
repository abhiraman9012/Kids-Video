# File: google_drive/api_client.py
# Functions:
# - download_file_from_google_drive()
# - test_google_drive_api()

import os
import requests
import tempfile
import shutil
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import sys
import os
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DRIVE_CREDENTIALS_FILE_ID

# Create a global session for requests
session = requests.Session()

def download_file_from_google_drive(file_id, destination):
    """
    Downloads a file from Google Drive using its ID.
    
    Args:
        file_id (str): Google Drive file ID
        destination (str): Local path where file should be saved
        
    Returns:
        str: Path to the downloaded file
    """
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = session.get(url, stream=True)

    # Handle Google Drive's confirmation page for large files
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            url = f"https://drive.google.com/uc?id={file_id}&export=download&confirm={value}"
            response = session.get(url, stream=True)
            break

    # Save the file
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                
    print(f"✅ Downloaded file from Google Drive: {destination}")
    return destination

def test_google_drive_api():
    """
    Tests Google Drive API functionality (authentication, listing files, folder creation).
    
    Returns:
        bool: True if tests pass, False otherwise
    """
    print("⏳ Testing Google Drive API...")
    
    # Create temporary directory for credentials
    temp_dir = tempfile.mkdtemp()
    credentials_path = os.path.join(temp_dir, "credentials.json")
    token_path = os.path.join(temp_dir, "token.json")
    
    try:
        # Download credentials from Google Drive
        download_file_from_google_drive(DRIVE_CREDENTIALS_FILE_ID, credentials_path)
        
        # Set up credentials
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_info(json.loads(open(token_path).read()))
            
        # If there are no (valid) credentials available, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, ['https://www.googleapis.com/auth/drive'])
                creds = flow.run_local_server(port=0)
                
            # Save credentials for future runs
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                
        # Build the service
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Test operations
        
        # List files
        results = drive_service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            print("No files found in Google Drive.")
        else:
            print(f"Found {len(items)} files in Google Drive.")
            
        # Create a test folder
        folder_metadata = {
            'name': 'Test Folder - Delete Me',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        test_folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        print(f"Created test folder with ID: {test_folder.get('id')}")
        
        # Clean up - delete the test folder
        drive_service.files().delete(fileId=test_folder.get('id')).execute()
        print("✅ Deleted test folder")
        
        print("✅ Google Drive API test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Google Drive API test failed: {e}")
        return False
        
    finally:
        # Clean up: Remove the temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"✅ Removed temporary directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️ Error cleaning up temp directory: {e}")
