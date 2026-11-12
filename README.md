# Twilio Demo Booking Dashboard

A simple Flask dashboard and Twilio voice webhook demo for outbound call booking.

## Features

- `/dashboard` UI with phone input and Call button
- `/trigger_call` API to launch a real or simulated outbound call
- `/voice` Twilio voice webhook with a multi-stage booking flow
- `/process` flow handler for DTMF input and booking persistence
- `student_bookings.json` stores demo bookings
- Simulation mode for local testing without a Twilio paid account

## Setup

1. Copy `.env.example` to `.env`.
2. Fill in your Twilio values, or set `SIMULATE_MODE=true` for local testing.

Example `.env`:

```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=+15551234567
VOICE_WEBHOOK_URL=http://localhost:5000/voice
SIMULATE_MODE=true
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python app.py
```

5. Open the dashboard:

```text
http://localhost:5000/dashboard
```

6. Enter a phone number and click **Call**.

## Simulation Mode

If `SIMULATE_MODE=true`, outbound call launching will POST to the configured `VOICE_WEBHOOK_URL` without using Twilio.

## Notes

- For real Twilio testing, expose your local server using ngrok and set `VOICE_WEBHOOK_URL` to the public webhook URL.
- `student_bookings.json` is updated whenever a booking is confirmed from the voice flow.
