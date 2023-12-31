from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    company_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    profile_pic = forms.ImageField(required=False)
    address = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    State = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['full_name', 'company_name', 'bio', 'profile_pic', 'address', 'State', 'phone']

class SearchForm(forms.Form):
    search_query = forms.CharField(label='Search', max_length=100)
