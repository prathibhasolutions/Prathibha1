from decimal import Decimal

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TechnologyBookingForm, TechnologyRescheduleForm
from .models import TechnologyBooking


TECHNOLOGY_OPTIONS = [
    'Peripherals and Sales',
    'Hardware Services',
    'Printer Services',
    'Cartridge Refilling',
    'Chip Level Services',
    'Networking',
    'AMC Services',
    'CC Camera Services',
    'Data Recovery',
]

TECHNOLOGY_PRICING = {
    'Peripherals and Sales': Decimal('499.00'),
    'Hardware Services': Decimal('799.00'),
    'Printer Services': Decimal('649.00'),
    'Cartridge Refilling': Decimal('399.00'),
    'Chip Level Services': Decimal('1199.00'),
    'Networking': Decimal('899.00'),
    'AMC Services': Decimal('1499.00'),
    'CC Camera Services': Decimal('1299.00'),
    'Data Recovery': Decimal('1799.00'),
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
            'receipt': f'tech-booking-{booking.id}',
            'payment_capture': 1,
        }
    )
    booking.razorpay_order_id = order['id']
    booking.payment_reference = order['id']
    booking.payment_status = TechnologyBooking.PAYMENT_STATUS_UNPAID
    booking.save(update_fields=['razorpay_order_id', 'payment_reference', 'payment_status'])
    return amount_paise


def technologies_home(request):
    return render(
        request,
        'technologies/home.html',
        {
            'technology_options': TECHNOLOGY_OPTIONS,
            'online_payment_enabled': is_online_payment_enabled(),
        },
    )


@login_required
def book_technology(request):
    selected_service = request.GET.get('service', '').strip()
    initial_data = {'service_name': selected_service}

    if request.method == 'POST':
        form = TechnologyBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user

            if booking.service_name not in TECHNOLOGY_OPTIONS:
                form.add_error('service_name', 'Please select a valid technology service.')
                return render(
                    request,
                    'technologies/book.html',
                    {
                        'form': form,
                        'technology_options': TECHNOLOGY_OPTIONS,
                        'online_payment_enabled': is_online_payment_enabled(),
                    },
                )

            booking.amount_inr = TECHNOLOGY_PRICING.get(booking.service_name, Decimal('499.00'))
            booking.payment_method = TechnologyBooking.PAYMENT_COD
            booking.payment_status = TechnologyBooking.PAYMENT_STATUS_UNPAID
            booking.payment_reference = 'COD'
            booking.address_line = 'N/A'
            booking.city = 'N/A'
            booking.pincode = '000000'
            booking.save()
            return redirect(f"{redirect('technologies:booking_success').url}?booking={booking.id}")
    else:
        form = TechnologyBookingForm(initial=initial_data)

    return render(
        request,
        'technologies/book.html',
        {
            'form': form,
            'technology_options': TECHNOLOGY_OPTIONS,
        },
    )


@login_required
def booking_success(request):
    booking_id = request.GET.get('booking')
    booking = None
    if booking_id:
        booking = TechnologyBooking.objects.filter(id=booking_id, user=request.user).first()
    return render(request, 'technologies/booking_success.html', {'booking': booking})


@login_required
def verify_online_payment(request):
    if request.method != 'POST':
        return redirect('technologies:home')

    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')
    booking_id = request.POST.get('booking_id', '')

    booking = TechnologyBooking.objects.filter(id=booking_id, user=request.user).first()
    if not booking:
        messages.error(request, 'Booking not found.')
        return redirect('technologies:home')

    if booking.status == TechnologyBooking.STATUS_CANCELLED:
        messages.error(request, 'Cancelled bookings cannot be paid.')
        return redirect('technologies:my_bookings')

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
        booking.payment_status = TechnologyBooking.PAYMENT_STATUS_FAILED
        booking.status = TechnologyBooking.STATUS_PENDING
        booking.save(update_fields=['payment_status', 'status'])
        messages.error(request, 'Payment verification failed. Please try again.')
        return redirect('technologies:my_bookings')

    booking.payment_status = TechnologyBooking.PAYMENT_STATUS_PAID
    booking.status = TechnologyBooking.STATUS_CONFIRMED
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

    return redirect(f"{redirect('technologies:booking_success').url}?booking={booking.id}")


@login_required
def my_bookings(request):
    bookings = TechnologyBooking.objects.filter(user=request.user)
    return render(
        request,
        'technologies/my_bookings.html',
        {
            'bookings': bookings,
            'online_payment_enabled': is_online_payment_enabled(),
        },
    )


@login_required
def retry_online_payment(request, booking_id):
    booking = get_object_or_404(TechnologyBooking, id=booking_id, user=request.user)

    if booking.payment_method != TechnologyBooking.PAYMENT_ONLINE:
        messages.info(request, 'Retry payment is available only for online payment bookings.')
        return redirect('technologies:my_bookings')

    if booking.payment_status == TechnologyBooking.PAYMENT_STATUS_PAID:
        messages.info(request, 'This booking is already paid.')
        return redirect('technologies:my_bookings')

    if booking.status in {TechnologyBooking.STATUS_CANCELLED, TechnologyBooking.STATUS_COMPLETED}:
        messages.error(request, 'Payment retry is not available for this booking status.')
        return redirect('technologies:my_bookings')

    if not is_online_payment_enabled():
        messages.error(request, 'Online payment setup is pending. Please use COD or configure payment keys.')
        return redirect('technologies:my_bookings')

    try:
        amount_paise = create_razorpay_order(booking)
    except Exception:
        messages.error(request, 'Unable to initiate payment retry. Please try again later.')
        return redirect('technologies:my_bookings')

    callback_url = request.build_absolute_uri('/technologies/verify-payment/')
    return render(
        request,
        'technologies/online_payment.html',
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
        return redirect('technologies:my_bookings')

    booking = get_object_or_404(TechnologyBooking, id=booking_id, user=request.user)
    if booking.status in {TechnologyBooking.STATUS_CANCELLED, TechnologyBooking.STATUS_COMPLETED}:
        messages.info(request, 'This booking cannot be cancelled.')
        return redirect('technologies:my_bookings')

    booking.status = TechnologyBooking.STATUS_CANCELLED
    booking.save(update_fields=['status'])
    messages.success(request, 'Booking cancelled successfully.')
    return redirect('technologies:my_bookings')


@login_required
def reschedule_booking(request, booking_id):
    booking = get_object_or_404(TechnologyBooking, id=booking_id, user=request.user)

    if booking.status in {TechnologyBooking.STATUS_CANCELLED, TechnologyBooking.STATUS_COMPLETED}:
        messages.info(request, 'This booking cannot be rescheduled.')
        return redirect('technologies:my_bookings')

    if request.method == 'POST':
        form = TechnologyRescheduleForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking rescheduled successfully.')
            return redirect('technologies:my_bookings')
    else:
        form = TechnologyRescheduleForm(instance=booking)

    return render(
        request,
        'technologies/reschedule.html',
        {
            'form': form,
            'booking': booking,
        },
    )
