from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Appointment

User = get_user_model()


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = (
            'patient_name',
            'contact_number',
            'appointment_date',
            'appointment_time',
            'purpose',
            'status',
        )
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'purpose': forms.Textarea(attrs={'rows': 4}),
        }


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, label='Full name')
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('full_name', 'username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data['full_name'].strip().split()
        user.first_name = full_name[0] if full_name else ''
        user.last_name = ' '.join(full_name[1:])
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
