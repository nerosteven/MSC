from django.shortcuts import render, redirect
from .models import Plan, Coordinate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
import json
import pyproj
from .models import Plan, Coordinate, UserMap
import folium
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from pyproj import Transformer
from django.contrib.admin.views.decorators import staff_member_required
from geopy.geocoders import Nominatim
from leaflet.forms.widgets import LeafletWidget
import csv
from django.http import HttpResponse
from geopy.geocoders import Nominatim  # Geocoding library
from .forms import UserUpdateForm, ProfileUpdateForm  # Import your forms
from django.db.models import Q
from .forms import SearchForm
from .models import Profile


@login_required
def add_plan(request):
    if request.method == 'POST':
        try:
            # Get data from the form and create the Plan and Coordinate objects
            plannumber = request.POST.get('plannumber')
            area = request.POST.get('area')
            location = request.POST.get('location')
            surveyor = request.POST.get('surveyor')
            coordinatesystem = request.POST.get('coordinatesystem')
            date = request.POST.get('date')
            num_coordinates = int(request.POST.get('num_coordinates'))

            # Create the plan object
            plan = Plan(plannumber=plannumber, area=area, location=location,
                        surveyor=surveyor, coordinatesystem=coordinatesystem, date=date)
            plan.save()

            # Create the coordinate objects
            coordinates_data = []  # List to store the coordinates for plotting
            for i in range(num_coordinates):
                pillarnumber = request.POST.getlist('pillarnumber[]')[i]
                eastings = float(request.POST.getlist('eastings[]')[i])  # Convert to float
                northings = float(request.POST.getlist('northings[]')[i])  # Convert to float

                # Convert UTM coordinates (eastings and northings) to latitude and longitude
                utm_zone_number = 32  # Replace this with the appropriate UTM zone number
                p = pyproj.Proj(proj='utm', zone=utm_zone_number, ellps='clrk80', datum='NAD83')
                lon, lat = p(eastings, northings, inverse=True)
                coord = Coordinate(plan=plan, pillarnumber=pillarnumber, eastings=eastings, northings=northings,
                                latitude=lat, longitude=lon)
                coord.save()

                # Append the coordinate data for plotting
                coordinates_data.append({'pillarnumber': pillarnumber, 'lat': lat, 'lon': lon})

            # Redirect to a view that displays the map with the plotted coordinates
            return redirect('display_map', plannumber=plannumber)  # Change 'display_map' to your actual view name
        except (IntegrityError, ValueError) as e:
            error_message = str(e)
            return render(request, 'add_plan.html', {'error_message': error_message})

    return render(request, 'add_plan.html')

# views.py
@login_required
def query_plan(request):
    if request.method == 'POST':
        # Get pillarnumber from the form
        pillarnumber = request.POST.get('pillarnumber')

        # Query the database
        coords = Coordinate.objects.filter(pillarnumber=pillarnumber)

        if coords.exists():
            # Get the plan associated with the coordinates
            plan = coords.first().plan

            return render(request, 'query_result.html', {'plan': plan, 'coords': coords})
        else:
            # If no coordinates are found, add a message to the user
            messages.error(request, 'There is no pillar number with that number.')
            return render(request, 'query_plan.html', {'message': 'No records found.'})

    return render(request, 'query_plan.html')

def query_result(request):
    pillarnumber = request.GET.get('pillarnumber')
    coordinates = Coordinate.objects.filter(pillarnumber=pillarnumber)
    context = {'coordinates': coordinates}
    return render(request, 'query_result.html', context)


def home(request):
    return render(request, 'home.html')

def display_map(request, plannumber):
    try:
        plan = Plan.objects.get(plannumber=plannumber)
        coordinates = Coordinate.objects.filter(plan=plan)

        # Extract latitude and longitude coordinates from the Coordinate objects
        coordinates_data = [{'lat': coord.latitude, 'lon': coord.longitude} for coord in coordinates]
        
        # Calculate the center of the map based on the first coordinate
        if coordinates_data:
            center_lat = coordinates_data[0]['lat']
            center_lon = coordinates_data[0]['lon']
        else:
            # Default center if no coordinates are available
            center_lat = 0
            center_lon = 0

        return render(request, 'display_map.html', {
            'plannumber': plannumber,
            'coordinates_data': coordinates_data,
            'center_lat': center_lat,
            'center_lon': center_lon,
        })
    except Plan.DoesNotExist:
        # Handle the case where the specified plan does not exist
        return render(request, 'display_map.html', {
            'error_message': f"Plan with plannumber '{plannumber}' does not exist."
        })


def download_csv(request):
    pillarnumber = request.GET.get('pillarnumber')
    plan = Plan.objects.filter(plannumber=pillarnumber).first()
    coordinates = Coordinate.objects.filter(plan=plan)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="query_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Plan number', 'Area', 'Location', 'Surveyor', 'Coordinate system', 'Date', 'Number of coordinates'])
    
    if plan:
        writer.writerow([plan.plannumber, plan.area, plan.location, plan.surveyor, plan.coordinatesystem, plan.date, coordinates.count()])
    else:
        writer.writerow(['No plan found for the given pillarnumber.'])
    
    writer.writerow([])
    writer.writerow(['Pillar number', 'Eastings', 'Northings'])
    
    for coord in coordinates:
        writer.writerow([coord.pillarnumber, coord.eastings, coord.northings])
    
    return response

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            
            profile = profile_form.save(commit=False)
            profile.user = request.user

            # Geocode the address and populate latitude and longitude
            geolocator = Nominatim(user_agent="myGeocoder")
            location = geolocator.geocode(profile.address)
            if location:
                profile.latitude = location.latitude
                profile.longitude = location.longitude

            profile.save()
            
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'update_profile.html', context)

@login_required
def profile(request):
  profile = request.user.profile

  context = {
    'profile': profile
  }

  return render(request, 'profile.html', context)

@login_required
def profile(request):
  profile = request.user.profile

  context = {
    'profile': profile
  }

  return render(request, 'profile.html', context)

@login_required
def search_surveyors(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
            search_results = Profile.objects.filter(
                Q(user__username__icontains=search_query) |
                Q(address__icontains=search_query)
            )
            return render(request, 'search_results.html', {'search_results': search_results})
    else:
        form = SearchForm()
    return render(request, 'search.html', {'form': form})

def view_map(request):
    user_profile = request.user.profile
    user_lat = user_profile.latitude
    user_lon = user_profile.longitude
    user_address = user_profile.address
    
    return render(request, 'view_map.html', {
        'user_lat': user_lat,
        'user_lon': user_lon,
        'user_address': user_address,
        'leaflet_widget': LeafletWidget(),
    })

