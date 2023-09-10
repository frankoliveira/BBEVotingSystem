from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from orderer import views

urlpatterns = [
    path('pending-transactions/', views.PendingTransactionList.as_view()),
    path('confirmed-transactions/<str:pk>/', views.ConfirmedTransactionDetail.as_view()),
    path('mine-block/', views.BlockMining.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns) 