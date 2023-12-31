from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.validators import MinValueValidator, RegexValidator
from pyproj import Transformer
import pyproj

class Plan(models.Model):
    plannumber = models.CharField(db_column='PlanNumber', primary_key=True, max_length=50)  # Field name made lowercase.
    area = models.FloatField(db_column='Area', blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=255, blank=True, null=True)  # Field name made lowercase.
    surveyor = models.CharField(db_column='Surveyor', max_length=255, blank=True, null=True)  # Field name made lowercase.
    coordinatesystem = models.CharField(db_column='CoordinateSystem', max_length=255, blank=True, null=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'plan'
    def __str__(self):
        return self.plannumber


class Coordinate(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE, blank=True, null=True)
    pillarnumber = models.CharField(max_length=100, blank=False, validators=[
        RegexValidator(r'^[a-zA-Z0-9]+$', message='Pillar number must be alphanumeric')
    ])
    eastings = models.FloatField(null=False, validators=[
        MinValueValidator(0, message='Eastings must be a positive number')
    ])
    northings = models.FloatField(null=False, validators=[
        MinValueValidator(0, message='Northings must be a positive number')
    ])
    latitude = models.FloatField(null=True, blank=True)  # Latitude field
    longitude = models.FloatField(null=True, blank=True)  # Longitude field

    class Meta:
        db_table = 'coordinate'

    def __str__(self):
        return f"{self.pillarnumber} - ({self.eastings}, {self.northings})"


class UserMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    coordinates = models.ManyToManyField(Coordinate)
    map_data = models.TextField(blank=True, null=True)  # New field to store the map data as JSON

    class Meta:
        managed = True


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, default='')
    company_name = models.CharField(max_length=100, default='')
    bio = models.TextField(max_length=500, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    address = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=20, default='0000000000')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.user.username

