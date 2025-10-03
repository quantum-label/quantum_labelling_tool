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
    path('', home_view, name='home'),
    path('about', about_view, name='about'),
    path('login/', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('dashboard', user_dashboard_view, name='dashboard'),
    path('dataset/create', dataset_create_view, name='dataset_create'),
    path('dataset/modify', dataset_modify_view, name='dataset_modify'),
    path('dataset/delete', dataset_delete_view, name='dataset_delete'),
    path('dataset/label', dataset_label_view, name='dataset_label'),
    path('dataset/assessment', user_dataset_assessment_view, name='dataset_assessment'),
    path('dataset/assessment/rdf', download_assessment_rdf, name='dataset_assessment_rdf'),
    path('dataset/assessment/pdf', download_assessment_pdf, name='dataset_assessment_pdf'),
    path('catalogue/create', catalogue_create_view, name='catalogue_create'),
    path('catalogue/modify', catalogue_modify_view, name='catalogue_modify'),
    path('catalogue/delete', catalogue_delete_view, name='catalogue_delete'),
    path('organization/maturity', organization_maturity_view, name='organization_maturity'),
    path('organization/maturity/pdf', download_organization_maturity_pdf, name='organization_maturity_pdf'),
]
