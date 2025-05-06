# Salon Appointment Scheduler

An automated salon appointment scheduling system that handles bookings, confirmations, and follow-ups via email integration.

## Features

- Email monitoring for appointment requests
- Automated scheduling with Google Calendar integration
- Smart response system for booking confirmations and reminders
- Multi-stylist support
- Configurable business hours and services
- Admin interface for system configuration
- Appointment logging and management

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
Create a `.env` file with the following:
```
GMAIL_USER=your-email@gmail.com
GOOGLE_CALENDAR_ID=your-calendar-id
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

3. Set up Google API credentials:
- Enable Gmail API and Google Calendar API in Google Cloud Console
- Download credentials.json and place it in the project root
- Run the authentication script: `python auth_setup.py`

4. Configure salon settings:
- Edit `config.py` with your salon's specific settings
- Set up business hours, services, and stylist information

5. Run the application:
```bash
python main.py
```

For the admin interface:
```bash
python admin.py
```

## Project Structure

- `main.py`: Application entry point
- `email_handler.py`: Email monitoring and processing
- `scheduler.py`: Appointment scheduling logic
- `calendar_manager.py`: Google Calendar integration
- `config.py`: Configuration settings
- `admin.py`: Admin interface
- `models.py`: Database models
- `templates/`: Email templates
- `utils/`: Utility functions

## Dependencies

- Python 3.x
- Google API Client Libraries
- Flask (for admin interface)
- SQLAlchemy (for database)
- Additional dependencies in requirements.txt

## License

MIT License 