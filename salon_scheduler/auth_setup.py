import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar'
]

def setup_credentials():
    """Set up Google API credentials for Gmail and Calendar access."""
    creds = None
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json file not found!")
                print("\nPlease follow these steps:")
                print("1. Go to the Google Cloud Console (https://console.cloud.google.com)")
                print("2. Create a new project or select an existing one")
                print("3. Enable the Gmail API and Google Calendar API")
                print("4. Go to the Credentials page")
                print("5. Create an OAuth 2.0 Client ID (type: Desktop app)")
                print("6. Download the client configuration file")
                print("7. Rename it to 'credentials.json' and place it in this directory")
                print("\nThen run this script again.")
                return False

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        print("Authentication successful! Credentials saved to 'token.json'")
        return True

    print("Existing credentials are valid.")
    return True

def create_env_file():
    """Create .env file with necessary configuration."""
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json file not found!")
        return False

    with open('credentials.json', 'r') as f:
        creds_data = json.load(f)
        client_id = creds_data['installed']['client_id']
        client_secret = creds_data['installed']['client_secret']

    env_content = f"""GMAIL_USER=your-email@gmail.com
GOOGLE_CALENDAR_ID=your-calendar-id
GOOGLE_CLIENT_ID={client_id}
GOOGLE_CLIENT_SECRET={client_secret}
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("\nCreated .env file with Google API credentials.")
    print("Please edit the file and set your Gmail address and Calendar ID.")
    return True

def main():
    """Run the authentication setup process."""
    print("Setting up Google API authentication...")
    
    if setup_credentials():
        create_env_file()
        print("\nSetup complete! You can now run the salon scheduler.")
    else:
        print("\nSetup failed. Please check the error messages above.")

if __name__ == '__main__':
    main() 