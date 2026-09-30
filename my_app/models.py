from django.db import models


class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    patient_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    purpose = models.CharField(max_length=255)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return self.patient_name