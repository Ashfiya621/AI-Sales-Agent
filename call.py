import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv(override=True)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER')
VOICE_WEBHOOK_URL = os.getenv('VOICE_WEBHOOK_URL') or 'http://localhost:5000/voice'
SIMULATE_MODE = os.getenv('SIMULATE_MODE', 'false').lower() in ('1', 'true', 'yes')


def start_outbound_call(to_phone):
    if SIMULATE_MODE or not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return simulate_call(to_phone)

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        twiml=f'<Response><Say>Connecting your demo booking session.</Say><Gather numDigits="1" action="{VOICE_WEBHOOK_URL}/process" timeout="10"><Say>Press 1 to continue.</Say></Gather></Response>',
        to=to_phone,
        from_=TWILIO_FROM_NUMBER,
        url=VOICE_WEBHOOK_URL,
    )
    return {'status': 'started', 'sid': call.sid, 'mode': 'live', 'to': to_phone}


def simulate_call(to_phone):
    if not VOICE_WEBHOOK_URL:
        return {'status': 'failed', 'message': 'VOICE_WEBHOOK_URL is not configured for simulation.'}
    payload = {
        'CallSid': 'SIMULATED_CALL',
        'From': to_phone,
        'To': TWILIO_FROM_NUMBER or 'SIMULATED_FROM',
        'CallStatus': 'ringing',
    }
    try:
        response = requests.post(VOICE_WEBHOOK_URL, data=payload, timeout=10)
        return {
            'status': 'simulated',
            'to': to_phone,
            'mode': 'simulate',
            'webhook_response': response.text[:1024],
            'http_status': response.status_code,
        }
    except requests.RequestException as exc:
        return {'status': 'failed', 'message': str(exc)}


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Launch an outbound Twilio call or simulate one.')
    parser.add_argument('phone', nargs='?', help='Destination phone number in E.164 format')
    args = parser.parse_args()

    if not args.phone:
        args.phone = input('Enter phone number (E.164 format): ').strip()

    if not args.phone:
        print('Phone number is required.')
    else:
        result = start_outbound_call(args.phone)
        print(result)
