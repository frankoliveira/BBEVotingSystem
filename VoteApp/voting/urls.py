from django.urls import path
from voting import views

urlpatterns = [
    path('', views.index, name='index'),
    path('eleicoes/', views.election_list, name='eleicoes'),
    path('eleicoes/<int:pk>/', views.election_details, name='detalhes-eleicao'),
    path('eleicoes/votar/<int:pk>/', views.election_vote, name='votar-eleicao'),

    path('gerenciador/eleicoes/', views.election_list_manager, name='gerenciar-eleicoes'),
    path('gerenciador/eleicoes/criar', views.election_creation_manager, name='criar-eleicao'),
    path('gerenciador/eleicoes/atualizar/<int:pk>/', views.election_update_manager, name='atualizar-eleicao'),

    path('gerenciador/eleicoes/<int:pk>/', views.election_details_manager, name='detalhes-eleicao-gerenciador'),
    path('gerenciador/eleicoes/apurar/<int:pk>/', views.election_vote_count, name='apurar-eleicao-gerenciador'),
    path('gerenciador/eleicoes/resultados/<int:pk>/', views.election_results_manager, name='contagem-eleicao-gerenciador'),
    
    path('eleicoes/parcial-results/', views.parcial_results, name='parcial-results'),
    path('eleicoes/candidatura/detalhes', views.candidacy_details, name='detalhes-candidatura')
]