from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reservation
from .forms import ReservationForm


@login_required
def reservation_create_view(request):
    """Create a new table reservation."""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.customer = request.user
            reservation.reservation_status = Reservation.Status.PENDING
            reservation.save()
            messages.success(
                request,
                f'Your reservation for {reservation.number_of_guests} guests on '
                f'{reservation.date.strftime("%B %d, %Y")} at '
                f'{reservation.time.strftime("%I:%M %p")} has been submitted! '
                f'We\'ll confirm it shortly.'
            )
            return redirect('reservations:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReservationForm()

    return render(request, 'reservations/reservation_form.html', {'form': form})


@login_required
def reservation_list_view(request):
    """List all reservations for the logged-in user."""
    reservations = Reservation.objects.filter(
        customer=request.user
    ).order_by('-date', '-time')

    context = {
        'reservations': reservations,
    }
    return render(request, 'reservations/reservation_list.html', context)


@login_required
def reservation_detail_view(request, pk):
    """View a specific reservation."""
    reservation = get_object_or_404(Reservation, pk=pk, customer=request.user)
    return render(request, 'reservations/reservation_detail.html', {'reservation': reservation})


@login_required
def reservation_cancel_view(request, pk):
    """Cancel a pending reservation."""
    reservation = get_object_or_404(Reservation, pk=pk, customer=request.user)

    if reservation.reservation_status in ['pending', 'confirmed']:
        reservation.reservation_status = Reservation.Status.CANCELLED
        reservation.save()
        messages.info(request, 'Your reservation has been cancelled.')
    else:
        messages.warning(request, 'This reservation cannot be cancelled.')

    return redirect('reservations:list')
