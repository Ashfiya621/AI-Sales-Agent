import json
from datetime import datetime
from pathlib import Path

BOOKING_FILE = Path(__file__).resolve().parent / 'student_bookings.json'


def load_bookings():
    if not BOOKING_FILE.exists():
        return []
    try:
        with BOOKING_FILE.open('r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_bookings(bookings):
    with BOOKING_FILE.open('w', encoding='utf-8') as f:
        json.dump(bookings, f, indent=2)


def add_booking(name, phone, course_key, source='voice'):
    bookings = load_bookings()
    booking = {
        'name': name,
        'phone': phone,
        'course_key': course_key,
        'source': source,
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    bookings.append(booking)
    save_bookings(bookings)
    return booking


def get_recent_bookings(limit=10):
    bookings = load_bookings()
    return bookings[-limit:][::-1]
