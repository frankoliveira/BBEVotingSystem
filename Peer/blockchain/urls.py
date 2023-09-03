from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from blockchain import views

urlpatterns = [
    path('blockchain/', views.blockchain_list), #cria uma blockchain com a inserção do loco genesis
    path('blockchain-blocks/', views.blockchain_block_list),
    path('blockchain-blocks/<int:pk>', views.blockchain_block_detail),
    path('blockchain-validity/', views.blockchain_validity)
]

urlpatterns = format_suffix_patterns(urlpatterns) 