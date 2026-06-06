import json
import math
import re
from decimal import Decimal

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookingRescheduleForm, ServiceBookingForm
from .models import ServiceBooking


SERVICE_OPTIONS = [
    'Electrician',
    'Carpenter',
    'Plumber',
    'Geyser Repair',
    'Washing Machine Repair',
    'Goods Carrier',
    'Water Purifier',
    'Painting',
    'Refrigerator Repair',
    'Tiles Work',
]

SERVICE_PRICING = {
    'Electrician': Decimal('499.00'),
    'Carpenter': Decimal('599.00'),
    'Plumber': Decimal('499.00'),
    'Geyser Repair': Decimal('699.00'),
    'Washing Machine Repair': Decimal('799.00'),
    'Goods Carrier': Decimal('999.00'),
    'Water Purifier': Decimal('549.00'),
    'Painting': Decimal('899.00'),
    'Refrigerator Repair': Decimal('899.00'),
    'Tiles Work': Decimal('1299.00'),
}

TECHNICIAN_GROUP_NAME = 'Technician'


def is_technician(user):
    return bool(
        user.is_authenticated and (
            user.is_superuser or user.groups.filter(name=TECHNICIAN_GROUP_NAME).exists()
        )
    )


def ensure_technician_access(request):
    if is_technician(request.user):
        return None

    if request.user.is_authenticated:
        messages.error(request, 'Only technicians can open the technician dashboard.')
        return redirect('services:my_bookings')

    return redirect('login')


def extract_coordinates(address_line):
    if not address_line:
        return None, None

    pattern = r'[-+]?\d+(?:\.\d+)?,[-+]?\d+(?:\.\d+)?'
    match = re.search(pattern, address_line)
    if not match:
        return None, None

    try:
        lat_text, lon_text = match.group(0).split(',')
        return Decimal(lat_text), Decimal(lon_text)
    except Exception:
        return None, None


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    d_phi = math.radians(float(lat2) - float(lat1))
    d_lambda = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def build_tracking_payload(booking):
    distance_km = None
    eta_minutes = None

    if (
        booking.customer_latitude is not None
        and booking.customer_longitude is not None
        and booking.technician_latitude is not None
        and booking.technician_longitude is not None
    ):
        distance_km = haversine_km(
            booking.customer_latitude,
            booking.customer_longitude,
            booking.technician_latitude,
            booking.technician_longitude,
        )
        eta_minutes = max(1, round((distance_km / 24) * 60))

    return {
        'booking_id': booking.id,
        'status': booking.status,
        'status_display': booking.get_status_display(),
        'technician_name': booking.technician.get_full_name() or booking.technician.username if booking.technician else 'Not assigned yet',
        'customer_latitude': float(booking.customer_latitude) if booking.customer_latitude is not None else None,
        'customer_longitude': float(booking.customer_longitude) if booking.customer_longitude is not None else None,
        'technician_latitude': float(booking.technician_latitude) if booking.technician_latitude is not None else None,
        'technician_longitude': float(booking.technician_longitude) if booking.technician_longitude is not None else None,
        'technician_location_updated_at': booking.technician_location_updated_at.isoformat() if booking.technician_location_updated_at else None,
        'distance_km': round(distance_km, 2) if distance_km is not None else None,
        'eta_minutes': eta_minutes,
        'customer_map_url': f"https://maps.google.com/?q={booking.customer_latitude},{booking.customer_longitude}" if booking.customer_latitude is not None and booking.customer_longitude is not None else None,
        'technician_map_url': f"https://maps.google.com/?q={booking.technician_latitude},{booking.technician_longitude}" if booking.technician_latitude is not None and booking.technician_longitude is not None else None,
    }


def is_online_payment_enabled():
    key_id = (settings.RAZORPAY_KEY_ID or '').strip()
    key_secret = (settings.RAZORPAY_KEY_SECRET or '').strip()

    placeholder_values = {
        'replace_with_razorpay_key_id',
        'replace_with_razorpay_key_secret',
        'your_key_id',
        'your_key_secret',
    }

    if not key_id or not key_secret:
        return False

    if key_id.lower() in placeholder_values or key_secret.lower() in placeholder_values:
        return False

    if key_id.lower().startswith('replace_') or key_secret.lower().startswith('replace_'):
        return False

    return True


def create_razorpay_order(booking):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_paise = int(booking.amount_inr * 100)
    order = client.order.create(
        {
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': f'booking-{booking.id}',
            'payment_capture': 1,
        }
    )
    booking.razorpay_order_id = order['id']
    booking.payment_reference = order['id']
    booking.payment_status = ServiceBooking.PAYMENT_STATUS_UNPAID
    booking.save(update_fields=['razorpay_order_id', 'payment_reference', 'payment_status'])
    return amount_paise


def services_home(request):
    return render(
        request,
        'services/home.html',
        {
            'service_options': SERVICE_OPTIONS,
            'online_payment_enabled': is_online_payment_enabled(),
            'is_technician_user': is_technician(request.user),
        },
    )


@login_required
def book_service(request):
    selected_service = request.GET.get('service', '').strip()
    initial_data = {'service_name': selected_service}

    if request.method == 'POST':
        form = ServiceBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            if booking.service_name not in SERVICE_OPTIONS:
                form.add_error('service_name', 'Please select a valid service.')
                return render(
                    request,
                    'services/book.html',
                    {
                        'form': form,
                        'service_options': SERVICE_OPTIONS,
                    },
                )

            booking.amount_inr = SERVICE_PRICING.get(booking.service_name, Decimal('499.00'))
            booking.payment_method = ServiceBooking.PAYMENT_COD
            booking.payment_status = ServiceBooking.PAYMENT_STATUS_UNPAID
            booking.payment_reference = 'COD'
            booking.city = 'N/A'
            booking.pincode = '000000'

            if booking.customer_latitude is None or booking.customer_longitude is None:
                parsed_lat, parsed_lon = extract_coordinates(booking.address_line)
                if parsed_lat is not None and parsed_lon is not None:
                    booking.customer_latitude = parsed_lat
                    booking.customer_longitude = parsed_lon

            booking.save()
            return redirect(f"{redirect('services:booking_success').url}?booking={booking.id}")
    else:
        form = ServiceBookingForm(initial=initial_data)

    return render(
        request,
        'services/book.html',
        {
            'form': form,
            'service_options': SERVICE_OPTIONS,
        },
    )


@login_required
def booking_success(request):
    booking_id = request.GET.get('booking')
    booking = None
    if booking_id:
        booking = ServiceBooking.objects.filter(id=booking_id, user=request.user).first()
    return render(request, 'services/booking_success.html', {'booking': booking})


@login_required
def verify_online_payment(request):
    if request.method != 'POST':
        return redirect('services:home')

    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')
    booking_id = request.POST.get('booking_id', '')

    booking = ServiceBooking.objects.filter(id=booking_id, user=request.user).first()
    if not booking:
        messages.error(request, 'Booking not found.')
        return redirect('services:home')

    if booking.status == ServiceBooking.STATUS_CANCELLED:
        messages.error(request, 'Cancelled bookings cannot be paid.')
        return redirect('services:my_bookings')

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature(
            {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            }
        )
    except Exception:
        booking.payment_status = ServiceBooking.PAYMENT_STATUS_FAILED
        booking.status = ServiceBooking.STATUS_PENDING
        booking.save(update_fields=['payment_status', 'status'])
        messages.error(request, 'Payment verification failed. Please try again.')
        return redirect('services:my_bookings')

    booking.payment_status = ServiceBooking.PAYMENT_STATUS_PAID
    booking.status = ServiceBooking.STATUS_CONFIRMED
    booking.razorpay_order_id = razorpay_order_id
    booking.razorpay_payment_id = razorpay_payment_id
    booking.razorpay_signature = razorpay_signature
    booking.payment_reference = razorpay_payment_id
    booking.save(
        update_fields=[
            'payment_status',
            'status',
            'razorpay_order_id',
            'razorpay_payment_id',
            'razorpay_signature',
            'payment_reference',
        ]
    )

    return redirect(f"{redirect('services:booking_success').url}?booking={booking.id}")


@login_required
def my_bookings(request):
    bookings = ServiceBooking.objects.filter(user=request.user)
    return render(
        request,
        'services/my_bookings.html',
        {
            'bookings': bookings,
            'online_payment_enabled': is_online_payment_enabled(),
            'trackable_statuses': {
                ServiceBooking.STATUS_CONFIRMED,
                ServiceBooking.STATUS_ACCEPTED,
                ServiceBooking.STATUS_ON_THE_WAY,
            },
        },
    )


@login_required
def track_booking(request, booking_id):
    booking = get_object_or_404(ServiceBooking, id=booking_id, user=request.user)
    return render(
        request,
        'services/track_booking.html',
        {
            'booking': booking,
            'tracking': build_tracking_payload(booking),
        },
    )


@login_required
def booking_tracking_data(request, booking_id):
    booking = get_object_or_404(ServiceBooking, id=booking_id)

    if not (
        booking.user_id == request.user.id
        or request.user.is_staff
        or (booking.technician_id and booking.technician_id == request.user.id)
    ):
        return JsonResponse({'error': 'Not allowed'}, status=403)

    return JsonResponse(build_tracking_payload(booking))


def technician_dashboard(request):
    access_response = ensure_technician_access(request)
    if access_response is not None:
        return access_response

    incoming_bookings = ServiceBooking.objects.filter(
        status__in=[ServiceBooking.STATUS_PENDING, ServiceBooking.STATUS_CONFIRMED],
        technician__isnull=True,
    )
    my_active_bookings = ServiceBooking.objects.filter(
        technician=request.user,
        status__in=[
            ServiceBooking.STATUS_CONFIRMED,
            ServiceBooking.STATUS_ACCEPTED,
            ServiceBooking.STATUS_ON_THE_WAY,
        ],
    )

    return render(
        request,
        'services/technician_dashboard.html',
        {
            'incoming_bookings': incoming_bookings,
            'my_active_bookings': my_active_bookings,
        },
    )


def technician_accept_booking(request, booking_id):
    access_response = ensure_technician_access(request)
    if access_response is not None:
        return access_response

    if request.method != 'POST':
        return redirect('services:technician_dashboard')

    booking = get_object_or_404(ServiceBooking, id=booking_id)

    if booking.status in {ServiceBooking.STATUS_CANCELLED, ServiceBooking.STATUS_COMPLETED}:
        messages.info(request, 'This order cannot be accepted.')
        return redirect('services:technician_dashboard')

    if booking.technician_id and booking.technician_id != request.user.id:
        messages.error(request, 'This order is already accepted by another technician.')
        return redirect('services:technician_dashboard')

    booking.technician = request.user
    booking.accepted_at = booking.accepted_at or timezone.now()
    booking.status = ServiceBooking.STATUS_ACCEPTED
    booking.save(update_fields=['technician', 'accepted_at', 'status'])
    messages.success(request, 'Order accepted. Customer can now track your movement.')
    return redirect('services:technician_dashboard')


def technician_update_location(request, booking_id):
    if not is_technician(request.user):
        return JsonResponse({'error': 'Only technicians can update live location'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    booking = get_object_or_404(ServiceBooking, id=booking_id)
    if booking.technician_id != request.user.id:
        return JsonResponse({'error': 'You are not assigned to this order'}, status=403)

    if booking.status in {ServiceBooking.STATUS_CANCELLED, ServiceBooking.STATUS_COMPLETED}:
        return JsonResponse({'error': 'Tracking is disabled for this booking status'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        payload = request.POST

    latitude = payload.get('latitude')
    longitude = payload.get('longitude')
    if latitude in (None, '') or longitude in (None, ''):
        return JsonResponse({'error': 'latitude and longitude are required'}, status=400)

    try:
        booking.technician_latitude = Decimal(str(latitude))
        booking.technician_longitude = Decimal(str(longitude))
    except Exception:
        return JsonResponse({'error': 'Invalid coordinate values'}, status=400)

    booking.technician_location_updated_at = timezone.now()
    if booking.status == ServiceBooking.STATUS_ACCEPTED:
        booking.status = ServiceBooking.STATUS_ON_THE_WAY

    booking.save(
        update_fields=[
            'technician_latitude',
            'technician_longitude',
            'technician_location_updated_at',
            'status',
        ]
    )

    payload = build_tracking_payload(booking)
    payload['ok'] = True
    return JsonResponse(payload)


@login_required
def retry_online_payment(request, booking_id):
    booking = get_object_or_404(ServiceBooking, id=booking_id, user=request.user)

    if booking.payment_method != ServiceBooking.PAYMENT_ONLINE:
        messages.info(request, 'Retry payment is available only for online payment bookings.')
        return redirect('services:my_bookings')

    if booking.payment_status == ServiceBooking.PAYMENT_STATUS_PAID:
        messages.info(request, 'This booking is already paid.')
        return redirect('services:my_bookings')

    if booking.status in {ServiceBooking.STATUS_CANCELLED, ServiceBooking.STATUS_COMPLETED}:
        messages.error(request, 'Payment retry is not available for this booking status.')
        return redirect('services:my_bookings')

    if not is_online_payment_enabled():
        messages.error(request, 'Online payment setup is pending. Please use COD or configure payment keys.')
        return redirect('services:my_bookings')

    try:
        amount_paise = create_razorpay_order(booking)
    except Exception:
        messages.error(request, 'Unable to initiate payment retry. Please try again later.')
        return redirect('services:my_bookings')

    callback_url = request.build_absolute_uri('/services/verify-payment/')
    return render(
        request,
        'services/online_payment.html',
        {
            'booking': booking,
            'amount_paise': amount_paise,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'callback_url': callback_url,
        },
    )


@login_required
def cancel_booking(request, booking_id):
    if request.method != 'POST':
        return redirect('services:my_bookings')

    booking = get_object_or_404(ServiceBooking, id=booking_id, user=request.user)
    if booking.status in {ServiceBooking.STATUS_CANCELLED, ServiceBooking.STATUS_COMPLETED}:
        messages.info(request, 'This booking cannot be cancelled.')
        return redirect('services:my_bookings')

    booking.status = ServiceBooking.STATUS_CANCELLED
    booking.save(update_fields=['status'])
    messages.success(request, 'Booking cancelled successfully.')
    return redirect('services:my_bookings')


@login_required
def reschedule_booking(request, booking_id):
    booking = get_object_or_404(ServiceBooking, id=booking_id, user=request.user)

    if booking.status in {ServiceBooking.STATUS_CANCELLED, ServiceBooking.STATUS_COMPLETED}:
        messages.info(request, 'This booking cannot be rescheduled.')
        return redirect('services:my_bookings')

    if request.method == 'POST':
        form = BookingRescheduleForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking rescheduled successfully.')
            return redirect('services:my_bookings')
    else:
        form = BookingRescheduleForm(instance=booking)

    return render(
        request,
        'services/reschedule.html',
        {
            'form': form,
            'booking': booking,
        },
    )
