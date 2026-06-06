from django import forms

from .models import SolutionBooking


class SolutionBookingForm(forms.ModelForm):
    class Meta:
        model = SolutionBooking
        fields = [
            'service_name',
            'customer_name',
            'phone_number',
            'preferred_date',
            'preferred_time',
            'budget_range',
            'preferred_platform',
            'notes',
        ]
        widgets = {
            'service_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'customer_name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your project requirements'}),
        }
        labels = {
            'customer_name': 'Name',
            'preferred_platform': 'Preferred Delivery Type',
        }

    def clean_phone_number(self):
        value = self.cleaned_data['phone_number'].strip()
        if len(value) < 10:
            raise forms.ValidationError('Enter a valid phone number.')
        return value


class SolutionRescheduleForm(forms.ModelForm):
    class Meta:
        model = SolutionBooking
        fields = ['preferred_date', 'preferred_time', 'notes']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Update project details if needed'}),
        }
