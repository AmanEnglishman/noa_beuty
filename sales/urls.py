from django.urls import path
from . import views

urlpatterns = [
    path('today/', views.sales_today, name='sales_today'),
    path('new/', views.sale_create, name='sale_create'),
]
