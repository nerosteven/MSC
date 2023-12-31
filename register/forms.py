from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    surveyors_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'readonly': 'readonly'}))  # Add this line
    
    class Meta:
        model = User
        fields = ['username', 'email', 'surveyors_name']  # Include 'email' and 'surveyors_name' fields
        
class AuthForm(forms.Form):
  registration_number = forms.CharField()

  