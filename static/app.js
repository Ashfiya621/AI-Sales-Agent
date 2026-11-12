const phoneInput = document.getElementById('phone');
const callButton = document.getElementById('callButton');
const statusText = document.getElementById('statusText');
const spinner = document.getElementById('spinner');
const recentBookings = document.getElementById('recentBookings');

const setStatus = (message, loading = false) => {
  statusText.textContent = message;
  spinner.classList.toggle('hidden', !loading);
};

const renderBookings = (bookings) => {
  if (!bookings || bookings.length === 0) {
    recentBookings.innerHTML = '<p class="empty-state">No bookings yet.</p>';
    return;
  }

  recentBookings.innerHTML = bookings
    .map((booking) => `
      <div class="booking-card">
        <strong>${booking.course_key.replace(/\b\w/g, c => c.toUpperCase())}</strong>
        <p>${booking.phone}</p>
        <p>${new Date(booking.created_at).toLocaleString()}</p>
      </div>
    `)
    .join('');
};

const fetchBookings = async () => {
  try {
    const response = await fetch('/api/bookings');
    if (!response.ok) throw new Error('Failed to load bookings');
    const data = await response.json();
    renderBookings(data.bookings);
  } catch (error) {
    recentBookings.innerHTML = '<p class="empty-state">Unable to load bookings.</p>';
    console.error(error);
  }
};

const triggerCall = async (phone) => {
  setStatus('Connecting your call...', true);
  callButton.disabled = true;

  try {
    const response = await fetch('/trigger_call', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ phone }),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Call failed');
    }

    setStatus(`Call ${data.status} to ${data.to}.`);
    await fetchBookings();
  } catch (error) {
    setStatus(error.message || 'Unexpected error occurred.');
    console.error(error);
  } finally {
    callButton.disabled = false;
    spinner.classList.add('hidden');
  }
};

callButton.addEventListener('click', () => {
  const phone = phoneInput.value.trim();
  if (!phone) {
    setStatus('Please enter a valid phone number.');
    return;
  }
  triggerCall(phone);
});

window.addEventListener('DOMContentLoaded', () => {
  fetchBookings();
});
