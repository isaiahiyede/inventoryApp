from django.forms import ModelForm

from .models import *

# Create the form class.
class EmployeeCreationForm(ModelForm):
    class Meta:
        model = Employee
        fields = [
            "name",
            "email",
        ]
