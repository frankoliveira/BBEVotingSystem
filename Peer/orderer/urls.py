from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from orderer import views

urlpatterns = [
    path('pending-transactions/', views.PendingTransactionList.as_view()),
    path('create-consensus-block/', views.create_consensus_block)
]

urlpatterns = format_suffix_patterns(urlpatterns) 