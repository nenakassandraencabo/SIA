from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.appointment_list, name='appointment_list'),

    path(
        'add/',
        views.appointment_create,
        name='appointment_create'
    ),

    path(
        'edit/<int:id>/',
        views.appointment_update,
        name='appointment_update'
    ),

    path(
        'delete/<int:id>/',
        views.appointment_delete,
        name='appointment_delete'
    ),
]