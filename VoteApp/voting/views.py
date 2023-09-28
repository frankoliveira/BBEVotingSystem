from django.shortcuts import render, redirect
from voting.forms import ElectionCreateForm
from django.contrib import messages
from datetime import datetime

# Create your views here.
def criar_eleicao(request):
    if request.method == 'POST':
        print(request.POST)
        election_form = ElectionCreateForm(request.POST)
        if election_form.is_valid():
            election = election_form.save(commit=False)
            election.id_author = request.user
            election.creation = datetime.now()
            election.save()
            return redirect('index')
        messages.error(request, "Erro ao criar eleição")
    form = ElectionCreateForm()
    return render(request=request, template_name="election_form.html", context={"election_form": form})

def listar_eleicoes_ativas():
    pass

def votar():
    pass

#eleitor pode votar nas eleições em que for apto
#eleitor pode acessar eleições que participou
#eleitor pode acessar o resultado das eleições que participou
#eleitor pode ver os comprovantes de votação
#eleitor pode se conectar com um peer para checar o resultado das eleições,
#checar seu voto, verificar se o voto foi contabilizado e conferir os dados de uma eleição
#eleitor pode submeter um formulário para criação de uma eleição

#admin pode criar uma eleição
#admin pode editar eleição enquanto não estiver ocorrendo
#admin pode ver eleições que criou
#admin pode adicionar peer e ver os peers da rede p2p

#Other
import json, time
from hashlib import sha256
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import api_view

#Model
from voting.models import Election

#Serializer
from voting.serializers import ElectionSerializer

#inicia o consenso
@api_view(['GET']) 
def get_election(request, format=None):
    '''
    Essa lógica será executada de alguma forma pelo líder
    Aqui se inicia a proposta de bloco pelo líder
    '''
    if request.method == 'GET':
        try:
            election = Election.objects.last()
            if election:
                serializer = ElectionSerializer(instance=election)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            
            return Response(data='Não há eleições', status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(data=f"Erro na solicitação ccb:{ex}", status=status.HTTP_400_BAD_REQUEST)

from rest_framework import generics

class ElectionDetail(generics.RetrieveAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer

#inicia o consenso
@api_view(['POST']) 
def check_voting_permission(request, format=None):
    if request.method == 'POST':
        id_election = request.data['id_election']
        id_user = request.data['id_user']
        result = Election.check_voting_permission(id_election=id_election, id_user=id_user)

        return Response(data=f'Resultad: {result}', status=status.HTTP_200_OK)
