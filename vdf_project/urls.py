# vdf_project/urls.py
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from vdf_monitor.views import VDFListAPIView, LecturaListAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('api/vdfs/', VDFListAPIView.as_view(), name='vdf-list'),
    path('api/lecturas/', LecturaListAPIView.as_view(), name='lectura-list'),
]
