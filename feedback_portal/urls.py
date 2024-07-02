# feedback_portal/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reviews.urls')),  # Direct the root URL to the reviews app
]
