from django.urls import path
from users import views

urlpatterns = [
    path('registrar/', views.sign_up, name='registrar')
]