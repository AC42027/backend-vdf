# vdf_project/urls.py
from django.contrib import admin
from django.urls import path
from vdf_monitor.views import VDFListAPIView, LecturaListAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/vdfs/', VDFListAPIView.as_view(), name='vdf-list'),
    path('api/lecturas/', LecturaListAPIView.as_view(), name='lectura-list'),
]
