import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
import re
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List, Optional, Tuple

from config import (
    GMAIL_USER,
    EMAIL_TEMPLATES,
    SERVICES
)

class EmailHandler:
    def __init__(self, credentials_path: str = 'credentials.json'):
        self.credentials = Credentials.from_authorized_user_file(credentials_path, ['https://www.googleapis.com/auth/gmail.modify'])
        self.service = build('gmail', 'v1', credentials=self.credentials)
        self.jinja_env = Environment(loader=FileSystemLoader('templates'))

    def _create_message(self, to: str, subject: str, message_text: str, is_html: bool = True) -> dict:
        """Create a message for an email."""
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = GMAIL_USER
        message['subject'] = subject

        if is_html:
            msg = MIMEText(message_text, 'html')
        else:
            msg = MIMEText(message_text, 'plain')
        
        message.attach(msg)
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_email(self, to: str, subject: str, template_name: str, context: dict) -> bool:
        """Send an email using a template."""
        try:
            template = self.jinja_env.get_template(template_name)
            message_content = template.render(**context)
            message = self._create_message(to, subject, message_content)
            
            self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def parse_email_request(self, message_id: str) -> Tuple[dict, List[str]]:
        """Parse an email for appointment request details."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            email_data = {
                'from_email': next(h['value'] for h in headers if h['name'].lower() == 'from'),
                'subject': next(h['value'] for h in headers if h['name'].lower() == 'subject'),
                'date': next(h['value'] for h in headers if h['name'].lower() == 'date')
            }

            # Get email body
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                body = next(
                    (part['body']['data'] for part in parts if part['mimeType'] == 'text/plain'),
                    message['payload']['body'].get('data', '')
                )
            else:
                body = message['payload']['body'].get('data', '')

            decoded_body = base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8')

            # Extract information using regex patterns
            patterns = {
                'name': r'(?i)name:\s*([^\n]+)',
                'service': r'(?i)service:\s*([^\n]+)',
                'date': r'(?i)date:\s*([^\n]+)',
                'time': r'(?i)time:\s*([^\n]+)',
                'phone': r'(?i)phone:\s*([^\n]+)'
            }

            extracted_data = {}
            missing_fields = []

            for field, pattern in patterns.items():
                match = re.search(pattern, decoded_body)
                if match:
                    extracted_data[field] = match.group(1).strip()
                else:
                    missing_fields.append(field)

            # Validate service
            if 'service' in extracted_data:
                service = extracted_data['service'].lower()
                if service not in SERVICES:
                    missing_fields.append('valid_service')

            # Combine parsed data
            email_data.update(extracted_data)
            return email_data, missing_fields

        except Exception as e:
            print(f"Error parsing email: {str(e)}")
            return {}, ['error_parsing_email']

    def send_acknowledgment(self, to_email: str, client_name: str) -> bool:
        """Send an acknowledgment email for the appointment request."""
        context = {
            'client_name': client_name,
            'salon_name': 'Our Salon',  # Could be moved to config
            'current_year': datetime.now().year
        }
        return self.send_email(
            to_email,
            "We've Received Your Appointment Request",
            EMAIL_TEMPLATES['acknowledgment'],
            context
        )

    def send_confirmation(self, to_email: str, appointment_details: dict) -> bool:
        """Send a confirmation email with appointment details."""
        return self.send_email(
            to_email,
            "Your Appointment is Confirmed!",
            EMAIL_TEMPLATES['confirmation'],
            appointment_details
        )

    def send_reminder(self, to_email: str, appointment_details: dict) -> bool:
        """Send a reminder email for upcoming appointment."""
        return self.send_email(
            to_email,
            "Reminder: Your Upcoming Appointment",
            EMAIL_TEMPLATES['reminder'],
            appointment_details
        )

    def send_missing_info_request(self, to_email: str, missing_fields: List[str]) -> bool:
        """Send an email requesting missing information."""
        context = {
            'missing_fields': missing_fields,
            'services_list': list(SERVICES.keys())
        }
        return self.send_email(
            to_email,
            "Additional Information Needed for Your Appointment",
            EMAIL_TEMPLATES['missing_info'],
            context
        )

    def send_alternatives(self, to_email: str, client_name: str, 
                         requested_time: datetime, alternative_slots: List[datetime]) -> bool:
        """Send alternative time slots when requested time is unavailable."""
        context = {
            'client_name': client_name,
            'requested_time': requested_time,
            'alternative_slots': alternative_slots
        }
        return self.send_email(
            to_email,
            "Alternative Appointment Times Available",
            EMAIL_TEMPLATES['alternatives'],
            context
        )

    def monitor_inbox(self) -> List[dict]:
        """Monitor inbox for new appointment requests."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='in:inbox is:unread subject:"appointment request"'
            ).execute()

            messages = results.get('messages', [])
            new_requests = []

            for message in messages:
                email_data, missing_fields = self.parse_email_request(message['id'])
                if email_data:
                    new_requests.append({
                        'message_id': message['id'],
                        'data': email_data,
                        'missing_fields': missing_fields
                    })

                    # Mark as read
                    self.service.users().messages().modify(
                        userId='me',
                        id=message['id'],
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()

            return new_requests

        except Exception as e:
            print(f"Error monitoring inbox: {str(e)}")
            return [] 