import os
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from twilio.twiml.voice_response import Gather, VoiceResponse

from booking_system import add_booking, get_recent_bookings
from call import start_outbound_call
from course_booking import COURSES, find_course_by_digit, format_course_list

load_dotenv(override=True)

app = Flask(__name__, static_folder='static', template_folder='templates')

TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER', '')
VOICE_WEBHOOK_URL = os.getenv('VOICE_WEBHOOK_URL', '')
SIMULATE_MODE = os.getenv('SIMULATE_MODE', 'false').lower() in ('1', 'true', 'yes')

call_sessions = {}


def normalize_phone(phone):
    if not phone:
        return None
    return phone.strip()


def make_gather(message, action='/process', num_digits=1):
    response = VoiceResponse()
    gather = Gather(action=action, num_digits=num_digits, timeout=8)
    gather.say(message)
    response.append(gather)
    response.say('We did not receive input. Goodbye.')
    response.hangup()
    return response


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


@app.route('/api/bookings')
def api_bookings():
    return jsonify({'bookings': get_recent_bookings(10)})


@app.route('/trigger_call', methods=['POST'])
def trigger_call():
    payload = request.get_json() or request.form
    phone = normalize_phone(payload.get('phone'))
    if not phone:
        return jsonify({'status': 'error', 'message': 'Phone number is required.'}), 400

    result = start_outbound_call(phone)
    status_code = 200 if result.get('status') in ('started', 'simulated') else 500
    return jsonify(result), status_code


@app.route('/voice', methods=['GET', 'POST'])
def voice():
    call_sid = request.values.get('CallSid', 'SIMULATED_CALL')
    from_number = request.values.get('From', '')
    stage = request.values.get('stage') or call_sessions.get(call_sid, {}).get('stage', 'start')

    if stage == 'start':
        call_sessions[call_sid] = {'stage': 'choice', 'from': from_number}
        return str(make_gather('Welcome to the demo booking service. Press 1 to book a demo or press 2 to hear course options.'))

    return str(make_gather('Please press 1 to book a demo or press 2 for course information.'))


@app.route('/process', methods=['POST'])
def process():
    call_sid = request.values.get('CallSid', 'SIMULATED_CALL')
    digits = request.values.get('Digits', '').strip()
    session = call_sessions.setdefault(call_sid, {'stage': 'choice', 'from': request.values.get('From', '')})
    response = VoiceResponse()

    if session['stage'] == 'choice':
        if digits == '1':
            session.update({'stage': 'confirm', 'course_key': 'design'})
            response.say('You selected booking. Press 1 to confirm your demo reservation, or 2 to cancel.')
            response.gather(num_digits=1, action='/process', timeout=8)
            return str(response)
        if digits == '2':
            response.say('Here are our available courses.')
            for idx, course in enumerate(COURSES, start=1):
                response.say(f'Course {idx}: {course["name"]}. {course["description"]}')
            response.say('Thank you for calling. Goodbye.')
            response.hangup()
            return str(response)
        response.say('Sorry, that choice is invalid.')
        response.append(make_gather('Press 1 to book a demo or press 2 to hear course options.'))
        return str(response)

    if session['stage'] == 'confirm':
        if digits == '1':
            add_booking('Demo Caller', session.get('from', 'unknown'), session.get('course_key', 'design'), source='voice')
            response.say('Your demo booking is confirmed. We will follow up soon. Goodbye.')
            response.hangup()
            call_sessions.pop(call_sid, None)
            return str(response)
        response.say('Your booking request was canceled. Goodbye.')
        response.hangup()
        call_sessions.pop(call_sid, None)
        return str(response)

    response.say('We could not process your request. Goodbye.')
    response.hangup()
    call_sessions.pop(call_sid, None)
    return str(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
