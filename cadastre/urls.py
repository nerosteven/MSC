from django.urls import path, include
from . import views
from register import views as register_views
from .views import download_csv

urlpatterns = [
  path('register/', register_views.register, name='register'),
  path('', register_views.authenticate, name='authenticate'),
  path('register/<str:registration_number>/', register_views.register_with_number, name='register_with_number'),
  path('home/', views.home, name='home'),
  path('query_plan/', views.query_plan, name='query_plan'),
  path('query_result/', views.query_result, name='query_result'),
  path('accounts/', include('django.contrib.auth.urls')),
  path('add_plan/', views.add_plan, name='add_plan'),  
  path('display_map/<path:plannumber>/', views.display_map, name='display_map'),
  path('download_csv/', download_csv, name='download_csv'),
  path('update_profile/', views.update_profile, name='update_profile'),
  path('profile/', views.profile, name='profile'),
  path('search/', views.search_surveyors, name='search_surveyors'),
  path('view_map/', views.view_map, name='view_map'),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)