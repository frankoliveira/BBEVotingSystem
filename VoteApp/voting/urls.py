from django.urls import path
from voting import views

urlpatterns = [
    path('', views.index, name='index'),
    path('eleicoes/', views.election_list, name='eleicoes'),
    path('eleicoes/criar', views.criar_eleicao, name='criar-eleicao'),
    path('eleicoes/votar/<int:pk>/', views.election_vote, name='votar-eleicao')
]