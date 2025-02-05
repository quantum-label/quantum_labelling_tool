"""
URL configuration for quantum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from webapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),
    path('about', about_view),
    path('glossary', glossary_view),
    path('login', login_view),
    path('logout', logout_view),
    path('dashboard', user_dashboard_view),
    path('dataset/create', dataset_create_view),
    path('dataset/modify', dataset_modify_view),
    path('dataset/delete', dataset_delete_view),
    path('dataset/label', dataset_label_view),
    path('dataset/assessment', user_dataset_assessment_view),
    path('dataset/assessment/rdf', download_assessment_rdf),
    path('catalogue/create', catalogue_create_view),
    path('catalogue/modify', catalogue_modify_view),
    path('catalogue/delete', catalogue_delete_view),
    path('organization/maturity', organization_maturity_view)
]
