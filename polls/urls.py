from django.urls import path
from . import views

urlpatterns = [
    path('', views.poll_list_view, name='poll_list'),
    path('poll/create/', views.poll_create_view, name='poll_create'),
    path('poll/<int:pk>/', views.poll_detail_view, name='poll_detail'),
    path('poll/<int:pk>/vote/', views.vote_api_view, name='vote_api'),
    path('poll/<int:pk>/toggle/', views.toggle_poll_status_view, name='toggle_poll_status'),
    path('poll/<int:pk>/delete/', views.delete_poll_view, name='delete_poll'),
]
