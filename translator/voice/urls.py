from django.urls import path
from .views import home, translate_audio

urlpatterns = [
    path('', home),
    path('translate/', translate_audio),
]