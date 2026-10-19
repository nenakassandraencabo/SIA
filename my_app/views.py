from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import AppointmentForm, RegistrationForm
from .models import Appointment


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('appointment_list')

    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_short_name() or user.username}.')
            next_url = request.POST.get('next') or request.GET.get('next', '')
            if url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('appointment_list')
        error = 'The username or password you entered is incorrect.'

    return render(request, 'login.html', {'error': error, 'next': request.GET.get('next', '')})


def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('appointment_list')

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your account is ready. Log in to manage appointments.')
        return redirect('login')
    return render(request, 'register.html', {'form': form})


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def appointment_list(request: HttpRequest) -> HttpResponse:
    all_appointments = Appointment.objects.all()
    status_counts = all_appointments.aggregate(
        total=Count('appointment_id'),
        pending=Count('appointment_id', filter=Q(status='Pending')),
        approved=Count('appointment_id', filter=Q(status='Confirmed')),
        cancelled=Count('appointment_id', filter=Q(status='Cancelled')),
    )
    appointments = all_appointments

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    if query:
        search_filter = (
            Q(patient_name__icontains=query)
            | Q(contact_number__icontains=query)
            | Q(purpose__icontains=query)
        )
        if query.isdecimal():
            search_filter |= Q(appointment_id=int(query))
        appointments = appointments.filter(search_filter)
    valid_statuses = {value for value, _label in Appointment.STATUS_CHOICES}
    if status in valid_statuses:
        appointments = appointments.filter(status=status)

    return render(request, 'dashboard.html', {
        'appointments': appointments.order_by('appointment_date', 'appointment_time'),
        'status_choices': Appointment.STATUS_CHOICES,
        'search_query': query,
        'selected_status': status,
        **status_counts,
    })


@login_required
def appointment_create(request: HttpRequest) -> HttpResponse:
    form = AppointmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Appointment added successfully.')
        return redirect('appointment_list')
    return render(request, 'appointment_form.html', {'form': form})


@login_required
def appointment_update(request: HttpRequest, id: int) -> HttpResponse:
    appointment = get_object_or_404(Appointment, appointment_id=id)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Appointment updated successfully.')
        return redirect('appointment_list')
    return render(request, 'appointment_form.html', {'form': form, 'appointment': appointment})


@login_required
def appointment_delete(request: HttpRequest, id: int) -> HttpResponse:
    appointment = get_object_or_404(Appointment, appointment_id=id)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully.')
        return redirect('appointment_list')
    return render(request, 'appointment_confirm_delete.html', {'appointment': appointment})