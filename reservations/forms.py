from django import forms
from .models import Reservation
import datetime


class ReservationForm(forms.ModelForm):
    """Form for booking a table reservation."""

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': datetime.date.today().isoformat(),
        }),
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'min': '10:00',
            'max': '22:00',
        }),
    )

    class Meta:
        model = Reservation
        fields = ['date', 'time', 'number_of_guests', 'special_request']
        widgets = {
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of Guests',
                'min': 1,
                'max': 20,
            }),
            'special_request': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any special requests? (dietary needs, occasion, etc.)',
                'rows': 3,
            }),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.date.today():
            raise forms.ValidationError('Reservation date cannot be in the past.')
        # Allow booking up to 30 days in advance
        if date > datetime.date.today() + datetime.timedelta(days=30):
            raise forms.ValidationError('Reservations can be made up to 30 days in advance.')
        return date

    def clean_time(self):
        time = self.cleaned_data['time']
        opening = datetime.time(10, 0)
        closing = datetime.time(22, 0)
        if time < opening or time > closing:
            raise forms.ValidationError('Reservation time must be between 10:00 AM and 10:00 PM.')
        return time
