from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pytz

from config import (
    DATABASE_URL,
    CALENDAR_TIMEZONE,
    SERVICES,
    STYLISTS,
    BUSINESS_HOURS
)
from models import Client, Appointment, Service, Stylist, AppointmentStatus
from scheduler import Scheduler

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Database setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
scheduler = Scheduler()

@app.route('/')
def dashboard():
    """Display the main dashboard."""
    session = Session()
    today = datetime.now(pytz.timezone(CALENDAR_TIMEZONE))
    
    # Get today's appointments
    todays_appointments = session.query(Appointment).filter(
        Appointment.start_time >= today.replace(hour=0, minute=0),
        Appointment.start_time < (today + timedelta(days=1)).replace(hour=0, minute=0)
    ).all()
    
    # Get upcoming appointments for the week
    upcoming_appointments = scheduler.get_upcoming_appointments(7)
    
    # Get basic stats
    total_clients = session.query(Client).count()
    total_appointments = session.query(Appointment).count()
    
    session.close()
    
    return render_template(
        'dashboard.html',
        todays_appointments=todays_appointments,
        upcoming_appointments=upcoming_appointments,
        total_clients=total_clients,
        total_appointments=total_appointments
    )

@app.route('/appointments')
def appointments():
    """Display and manage appointments."""
    session = Session()
    appointments = session.query(Appointment).order_by(Appointment.start_time.desc()).all()
    session.close()
    return render_template('appointments.html', appointments=appointments)

@app.route('/clients')
def clients():
    """Display and manage clients."""
    session = Session()
    clients = session.query(Client).all()
    session.close()
    return render_template('clients.html', clients=clients)

@app.route('/services')
def services():
    """Display and manage services."""
    return render_template('services.html', services=SERVICES)

@app.route('/stylists')
def stylists():
    """Display and manage stylists."""
    return render_template('stylists.html', stylists=STYLISTS)

@app.route('/schedule')
def schedule():
    """Display the scheduling interface."""
    return render_template(
        'schedule.html',
        services=SERVICES,
        stylists=STYLISTS,
        business_hours=BUSINESS_HOURS
    )

@app.route('/api/available-slots', methods=['POST'])
def get_available_slots():
    """API endpoint to get available appointment slots."""
    data = request.json
    service_name = data.get('service')
    date_str = data.get('date')
    stylist_id = data.get('stylist')
    
    try:
        preferred_date = datetime.strptime(date_str, '%Y-%m-%d').replace(
            tzinfo=pytz.timezone(CALENDAR_TIMEZONE)
        )
        slots = scheduler.find_available_slots(
            service_name,
            preferred_date=preferred_date,
            stylist_id=stylist_id
        )
        
        return jsonify({
            'slots': [
                {
                    'datetime': slot[0].isoformat(),
                    'stylists': slot[1]
                }
                for slot in slots
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/schedule-appointment', methods=['POST'])
def schedule_appointment():
    """API endpoint to schedule an appointment."""
    data = request.json
    try:
        appointment = scheduler.schedule_appointment(
            data['client_name'],
            data['service'],
            datetime.fromisoformat(data['datetime']),
            data['stylist_id']
        )
        return jsonify(appointment)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/cancel-appointment/<event_id>', methods=['POST'])
def cancel_appointment(event_id):
    """API endpoint to cancel an appointment."""
    try:
        success = scheduler.cancel_appointment(event_id)
        if success:
            session = Session()
            appointment = session.query(Appointment).filter_by(
                event_id=event_id
            ).first()
            if appointment:
                appointment.status = AppointmentStatus.CANCELLED
                session.commit()
            session.close()
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to cancel appointment'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/settings')
def settings():
    """Display and manage system settings."""
    return render_template('settings.html')

@app.template_filter('format_datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Template filter to format datetime objects."""
    if value is None:
        return ''
    return value.strftime(format)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 