from django.urls import path
from users import views

urlpatterns = [
    path('register/', views.sign_up, name='register'),
    path('cadastrar/', views.cadastrar, name='cadastrar')
]