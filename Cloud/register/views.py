from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.forms import UserCreationForm
import csv
from .forms import AuthForm


def authenticate_view(request):
  form = AuthForm()

  if request.method == 'POST':
    form = AuthForm(request.POST)
    if form.is_valid():
      registration_number = form.cleaned_data['registration_number']
      
      # Existing authentication logic
      valid_registration_numbers = set()
      with open('surveyors.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
          valid_registration_numbers.add(row['registration_number'])

      if registration_number in valid_registration_numbers:
        return redirect('register_with_number', registration_number=registration_number)
      else:
        messages.error(request, 'Invalid Registration Number')

  return render(request, 'authenticate.html', {'form': form})

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import UserRegisterForm
from cadastre.models import Profile

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, 'Account was successfully created: ' + user.username)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register/register.html', {'form': form})


def register_with_number(request, registration_number):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Create a profile for the user
            Profile.objects.create(user=user)
            messages.success(request, f'Account was successfully created: {user.username}')
            return redirect('login')
    else:
        # Get the user's name from the CSV and pre-fill the form
        surveyors_name = None
        with open('surveyors.csv', 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['registration_number'] == registration_number:
                    surveyors_name = row['surveyors_name']
                    break
        # Exit loop once surveyors_name is found
        if surveyors_name:
            initial_data = {'surveyors_name': surveyors_name, 'registration_number': registration_number}
            form = UserRegisterForm(initial=initial_data)
            form.fields['surveyors_name'].widget.attrs['readonly'] = True
        else:
            messages.error(request, 'User not found or invalid registration number')
            return redirect('authenticate')
    
    # Redirect to the authentication step
    return render(request, 'register/register.html', {'form': form})



from django.contrib.auth import authenticate, login

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR Password incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)

