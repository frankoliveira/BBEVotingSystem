from django.urls import path
from voting import views

urlpatterns = [
    path('', views.index, name='index'),
    path('eleicoes/', views.election_list, name='eleicoes'),
    path('eleicoes/<int:pk>/', views.election_details, name='detalhes-eleicao'),
    path('eleicoes/votar/<int:pk>/', views.election_vote, name='votar-eleicao'),

    #GET(lista eleições) | POST (criar)
    path('gerenciador/eleicoes/', views.election_list_manager, name='eleicoes-gerenciador'),
    #GET(lista cargos de uma eleição)
    path('gerenciador/eleicoes/<int:pk>/cargos/', views.election_position_list_manager, name='cargos-gerenciador'),
    #GET(lista eleitores de uma eleição)
    path('gerenciador/eleicoes/<int:pk>/eleitores/', views.election_voter_list_manager, name='eleitores-gerenciador'),
    path('gerenciador/eleicoes/<int:pk>/candidaturas/', views.election_candidacy_list_manager, name='candidaturas-gerenciador'),
    
    #GET(por id) | POST (atualizar)
    path('gerenciador/eleicoes/<int:pk>/', views.election_detail_manager, name='eleicao-gerenciador'),
    #POST(atualizar cargo)
    path('gerenciador/eleicoes/cargos/<int:pk>/', views.position_detail_manager, name='cargo-gerenciador'),
    #DELETE(por id)
    path('gerenciador/eleicoes/eleitores/<int:pk>/', views.election_voter_detail_manager, name='eleitor-gerenciador'),
    
    #Páginas para o formulário de criação
    path('gerenciador/eleicoes/criacao/', views.election_creation_manager, name='eleicoes-criacao-gerenciador'),
    path('gerenciador/eleicoes/<int:pk>/cargos/criacao/', views.election_position_creation_manager, name='cargos-criacao-gerenciador'),
    path('gerenciador/eleicoes/<int:pk>/eleitores/criacao/', views.election_voter_creation_manager, name='eleitores-criacao-gerenciador'),
    path('gerenciador/eleicoes/<int:pk>/candidaturas/criacao/', views.election_candidacy_creation_manager, 
         name='candidaturas-criacao-gerenciador'),

    #Páginas para o formulário de atualização
    path('gerenciador/eleicoes/atualizacao/<int:pk>/', views.election_update_manager, name='atualizacao-eleicao'),
    path('gerenciador/eleicoes/cargos/atualizacao/<int:pk>/', views.position_update_manager, name='cargo-atualizacao-gerenciador'),

    path('gerenciador/eleicoes/apurar/<int:pk>/', views.election_vote_count, name='apurar-eleicao-gerenciador'),
    #path('gerenciador/eleicoes/resultados/<int:pk>/', views.election_results_manager, name='contagem-eleicao-gerenciador'),
    
    path('eleicoes/parcial-results/', views.parcial_results, name='parcial-results'),
    path('eleicoes/candidatura/detalhes', views.candidacy_details, name='detalhes-candidatura')
]