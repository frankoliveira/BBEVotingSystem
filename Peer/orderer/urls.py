from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from orderer import views

urlpatterns = [
    path('transaction/', views.create_transaction)
]

urlpatterns = format_suffix_patterns(urlpatterns) 