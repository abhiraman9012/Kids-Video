# File: google_drive/uploader.py
# Functions:
# - upload_text_file_to_drive()
# - upload_video_to_drive()

import os
import json
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def upload_text_file_to_drive(content, filename, parent_folder_id=None):
    """
    Helper to upload text files to Google Drive.
    
    Args:
        content (str): Text content to upload
        filename (str): Name of the file to create
        parent_folder_id (str): ID of the parent folder (optional)
        
    Returns:
        str: Google Drive file ID
    """
    print(f"⏳ Uploading {filename} to Google Drive...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Set up credentials
        creds = None
        token_path = os.path.join(tempfile.gettempdir(), "token.json")
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_info(json.loads(open(token_path).read()))
            
        # If credentials are invalid, need to re-authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("⚠️ Drive API credentials not found or invalid")
                return None
        
        # Build the Drive service
        drive_service = build('drive', 'v3', credentials=creds)
        
        # File metadata
        file_metadata = {'name': filename}
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
            
        # Upload the file
        media = MediaFileUpload(temp_path, mimetype='text/plain')
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"✅ Uploaded {filename} to Google Drive with ID: {file.get('id')}")
        return file.get('id')
        
    except Exception as e:
        print(f"❌ Error uploading text file to Drive: {e}")
        return None
        
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_path)
        except Exception:
            pass

def upload_video_to_drive(video_path, metadata=None, thumbnail_path=None):
    """
    Uploads a video file to Google Drive along with metadata.
    
    Args:
        video_path (str): Path to the video file
        metadata (dict): Dictionary containing video metadata (title, description, tags)
        thumbnail_path (str): Path to the thumbnail image (optional)
        
    Returns:
        dict: Dictionary with Google Drive file IDs and direct download links
    """
    print("⏳ Uploading video to Google Drive...")
    
    try:
        # Set up credentials
        creds = None
        token_path = os.path.join(tempfile.gettempdir(), "token.json")
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_info(json.loads(open(token_path).read()))
            
        # If credentials are invalid, need to re-authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("⚠️ Drive API credentials not found or invalid")
                return None
        
        # Build the Drive service
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Create a parent folder for the video and related files
        folder_name = metadata.get('title', 'Generated Story Video') if metadata else 'Generated Story Video'
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"✅ Created folder in Google Drive with ID: {folder_id}")
        
        # Upload the video file
        video_file_metadata = {
            'name': os.path.basename(video_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
        video_file = drive_service.files().create(
            body=video_file_metadata,
            media_body=media,
            fields='id, webContentLink'
        ).execute()
        video_id = video_file.get('id')
        video_link = video_file.get('webContentLink', '')
        print(f"✅ Uploaded video to Google Drive with ID: {video_id}")
        
        # Upload thumbnail if provided
        thumbnail_id = None
        if thumbnail_path and os.path.exists(thumbnail_path):
            thumbnail_metadata = {
                'name': 'thumbnail.jpg',
                'parents': [folder_id]
            }
            thumbnail_media = MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
            thumbnail_file = drive_service.files().create(
                body=thumbnail_metadata,
                media_body=thumbnail_media,
                fields='id'
            ).execute()
            thumbnail_id = thumbnail_file.get('id')
            print(f"✅ Uploaded thumbnail to Google Drive with ID: {thumbnail_id}")
        
        # Upload metadata as JSON if provided
        metadata_id = None
        if metadata:
            metadata_content = json.dumps(metadata, indent=2)
            metadata_id = upload_text_file_to_drive(
                metadata_content,
                'metadata.json',
                folder_id
            )
            print(f"✅ Uploaded metadata to Google Drive with ID: {metadata_id}")
        
        result = {
            'folder_id': folder_id,
            'video_id': video_id,
            'video_link': video_link,
            'metadata_id': metadata_id,
            'thumbnail_id': thumbnail_id
        }
        
        return result
        
    except Exception as e:
        print(f"❌ Error uploading video to Drive: {e}")
        return None
