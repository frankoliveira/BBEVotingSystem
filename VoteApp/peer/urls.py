from django.urls import path
from peer import views

urlpatterns = [
    path('peer/', views.candidacy_details, name='detalhes-candidatura')
]