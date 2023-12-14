from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from orderer import views

urlpatterns = [
    path('pending-transactions/', views.pending_transaction),
    path('transactions/<str:pk>', views.get_confirmed_transaction),
    path('last-block-id/', views.get_last_block_id),
    path('block/<int:pk>', views.get_block),
    path('consensus/', views.create_consensus_block), #esse end-point será excluído
    path('pre-prepare/', views.pre_prepare),
    path('prepare/', views.prepare),
    path('commit/', views.commit),
    path('teste/', views.teste),
]

urlpatterns = format_suffix_patterns(urlpatterns) 