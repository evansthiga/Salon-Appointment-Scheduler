from datetime import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email Configuration
GMAIL_USER = os.getenv('GMAIL_USER')
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Business Hours (24-hour format)
BUSINESS_HOURS = {
    'Monday': {'start': time(9, 0), 'end': time(18, 0)},
    'Tuesday': {'start': time(9, 0), 'end': time(18, 0)},
    'Wednesday': {'start': time(9, 0), 'end': time(18, 0)},
    'Thursday': {'start': time(9, 0), 'end': time(18, 0)},
    'Friday': {'start': time(9, 0), 'end': time(18, 0)},
    'Saturday': {'start': time(9, 0), 'end': time(16, 0)},
    'Sunday': None  # Closed
}

# Services with durations (in minutes) and prices
SERVICES = {
    'haircut': {
        'duration': 45,
        'price': 50.00,
        'description': 'Basic haircut service'
    },
    'color': {
        'duration': 120,
        'price': 120.00,
        'description': 'Hair coloring service'
    },
    'styling': {
        'duration': 60,
        'price': 65.00,
        'description': 'Hair styling service'
    },
    'manicure': {
        'duration': 45,
        'price': 35.00,
        'description': 'Basic manicure service'
    }
}

# Stylists and their specializations
STYLISTS = {
    'alice': {
        'name': 'Alice Johnson',
        'specialties': ['haircut', 'color'],
        'schedule': BUSINESS_HOURS  # Uses default business hours
    },
    'bob': {
        'name': 'Bob Smith',
        'specialties': ['styling', 'color'],
        'schedule': BUSINESS_HOURS
    },
    'carol': {
        'name': 'Carol Williams',
        'specialties': ['manicure'],
        'schedule': BUSINESS_HOURS
    }
}

# Email Templates Configuration
EMAIL_TEMPLATES = {
    'acknowledgment': 'templates/acknowledgment.html',
    'confirmation': 'templates/confirmation.html',
    'reminder': 'templates/reminder.html',
    'missing_info': 'templates/missing_info.html',
    'alternatives': 'templates/alternatives.html'
}

# Database Configuration
DATABASE_URL = 'sqlite:///salon.db'

# Appointment Settings
MIN_ADVANCE_HOURS = 24  # Minimum hours in advance for booking
MAX_ADVANCE_DAYS = 30   # Maximum days in advance for booking
REMINDER_HOURS = 24     # Hours before appointment to send reminder

# Calendar Settings
CALENDAR_TIMEZONE = 'America/New_York'
SLOT_INTERVAL = 15  # Minutes between available slots

# Holiday Schedule (YYYY-MM-DD)
HOLIDAYS = [
    '2024-12-25',  # Christmas
    '2024-01-01',  # New Year's Day
    '2024-07-04',  # Independence Day
    # Add more holidays as needed
]

# Booking Rules
MAX_DAILY_APPOINTMENTS = 20  # Maximum appointments per day
BUFFER_BETWEEN_APPOINTMENTS = 15  # Minutes between appointments 