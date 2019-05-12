from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('teams/', views.teams, name='teams'),
    path('team/<int:id>', views.team_detail, name='team_detail'),
    path('players/', views.players, name='players'),
    path('player/<int:id>', views.player_detail, name='player_detail'),
]
