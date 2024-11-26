from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('delete-enterprise/<int:id>/', views.delete_enterprise, name='delete_enterprise'),
    path('delete-pollutant/<int:id>/', views.delete_pollutant, name='delete_pollutant'),
    path('delete-record/<int:id>/', views.delete_record, name='delete_record'),
    path('edit-enterprise/<int:id>/', views.edit_enterprise, name='edit_enterprise'),
    path('edit-pollutant/<int:id>/', views.edit_pollutant, name='edit_pollutant'),
    path('edit-record/<int:id>/', views.edit_record, name='edit_record'),
]


