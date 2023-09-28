from django.urls import path
from voting import views

urlpatterns = [
    path('eleicoes/', views.get_election),
    path('eleicao/<int:pk>', views.ElectionDetail.as_view()),
    path('eleicao/', views.criar_eleicao, name='criar-eleicao'),
    path('check/', views.check_voting_permission)
]