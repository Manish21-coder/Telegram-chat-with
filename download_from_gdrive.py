from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io

# Google Drive credentials (Use a service account)
GOOGLE_DRIVE_CREDENTIALS = "cobalt-howl-454616-m6-50d8d074c0f3.json"
FOLDER_ID = "18fCJJOtC0y_rGA3VglT4I9yozERcj60_"


# Google Drive Authentication
def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_DRIVE_CREDENTIALS, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)


def find_file_id(file_name, service):
    """Finds the file ID of a file with the given name in Google Drive."""
    query = f"name = '{file_name}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        print(f"No file named '{file_name}' found.")
        return None
    return files[0]['id']  # Return the first match


# Download file from Google Drive
def download_file(file_id, local_path, service):
    """Downloads a file from Google Drive and saves it locally."""
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    
    done = False
    while not done:
        _, done = downloader.next_chunk()

    with open(local_path, 'wb') as f:
        f.write(file.getvalue())
    print(f"File downloaded as {local_path}")


def upload_file(file_id, local_path, service, mime_type='text/csv'):
    """Replaces an existing file with an updated version."""
    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
    service.files().update(fileId=file_id, media_body=media).execute()
    print("File updated on Google Drive")

