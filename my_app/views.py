from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment


# =========================
# VIEW APPOINTMENTS
# =========================
def appointment_list(request):
    appointments = Appointment.objects.all()

    return render(request, 'dashboard.html', {
        'appointments': appointments
    })


# =========================
# ADD APPOINTMENT
# =========================
def appointment_create(request):

    if request.method == 'POST':

        patient_name = request.POST.get('patient_name')
        contact_number = request.POST.get('contact_number')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        purpose = request.POST.get('purpose')
        status = request.POST.get('status')

        Appointment.objects.create(
            patient_name=patient_name,
            contact_number=contact_number,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            purpose=purpose,
            status=status
        )

        return redirect('appointment_list')

    return render(request, 'appointment_form.html')


# =========================
# EDIT APPOINTMENT
# =========================
def appointment_update(request, id):

    appointment = get_object_or_404(Appointment, id=id)

    if request.method == 'POST':

        appointment.patient_name = request.POST.get('patient_name')
        appointment.contact_number = request.POST.get('contact_number')
        appointment.appointment_date = request.POST.get('appointment_date')
        appointment.appointment_time = request.POST.get('appointment_time')
        appointment.purpose = request.POST.get('purpose')
        appointment.status = request.POST.get('status')

        appointment.save()

        return redirect('appointment_list')

    return render(request, 'appointment_form.html', {
        'appointment': appointment
    })


# =========================
# DELETE APPOINTMENT
# =========================
def appointment_delete(request, id):

    appointment = get_object_or_404(Appointment, id=id)

    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')

    return render(request, 'appointment_confirm_delete.html', {
        'appointment': appointment
    })