from django.urls import path
from voting import views

urlpatterns = [
    path('', views.index, name='index'),
    path('eleicoes/', views.election_list, name='eleicoes'),
    path('eleicoes/criar', views.criar_eleicao, name='criar-eleicao'),
    path('eleicoes/<int:pk>/', views.election_details, name='detalhes-eleicao'),
    path('eleicoes/votar/<int:pk>/', views.election_vote, name='votar-eleicao'),
    path('eleicoes/parcial-results/', views.parcial_results, name='parcial-results'),

    path('eleicoes/candidatura/detalhes', views.candidacy_details, name='detalhes-candidatura')
]