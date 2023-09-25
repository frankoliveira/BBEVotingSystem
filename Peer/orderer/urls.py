from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from orderer import views

urlpatterns = [
    path('pending-transactions/', views.pending_transaction),
    path('consensus/', views.create_consensus_block),
    path('prepare/', views.prepare),
    path('commit/', views.commit),
]

urlpatterns = format_suffix_patterns(urlpatterns) 