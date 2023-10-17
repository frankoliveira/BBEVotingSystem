from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from orderer import views

urlpatterns = [
    path('pending-transactions/', views.pending_transaction),
    path('consensus/', views.create_consensus_block), #esse end-point será excluído
    path('pre-prepare/', views.pre_prepare),
    path('prepare/', views.prepare),
    path('commit/', views.commit),
]

urlpatterns = format_suffix_patterns(urlpatterns) 