from django import forms

from .models import ServiceBooking


class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = [
            'service_name',
            'customer_name',
            'phone_number',
            'address_line',
            'customer_latitude',
            'customer_longitude',
            'preferred_date',
            'preferred_time',
            'notes',
        ]
        widgets = {
            'service_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'customer_name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'address_line': forms.TextInput(
                attrs={
                    'readonly': 'readonly',
                    'placeholder': 'Select current location from map',
                }
            ),
            'customer_latitude': forms.HiddenInput(),
            'customer_longitude': forms.HiddenInput(),
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Any specific issue details'}),
        }
        labels = {
            'customer_name': 'Name',
            'address_line': 'Address (Current Location)',
        }

    def clean_phone_number(self):
        value = self.cleaned_data['phone_number'].strip()
        if len(value) < 10:
            raise forms.ValidationError('Enter a valid phone number.')
        return value


class BookingRescheduleForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = ['preferred_date', 'preferred_time', 'notes']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Update issue details if needed'}),
        }
