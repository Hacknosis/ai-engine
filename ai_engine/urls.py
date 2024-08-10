"""ai_engine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('api/report/segment_image', views.segment_image, name="segment_image"),
    path('api/report/process_report_quality', views.process_report_quality, name="process_report_quality"),
    path('api/report/process_report_tumor', views.process_report_tumor, name="process_report_tumor"),
    path('admin/', admin.site.urls),
    path('', views.index),
]
