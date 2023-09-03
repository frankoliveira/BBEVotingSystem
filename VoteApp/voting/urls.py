from django.urls import path
from voting import views

urlpatterns = [
    path('eleicao/', views.criar_eleicao, name='register')
]