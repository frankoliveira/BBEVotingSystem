#Model
from voting.models import Election, Candidacy, ElectionVoter

#Forms
from voting.forms import ElectionCreateForm

#Serializer
from voting.serializers import ElectionSerializer, CandidacySerializer

#Django
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required

#Other
from datetime import datetime
from hashlib import sha256
from datetime import datetime

@login_required
def index(request):
    if request.method == 'GET':
        return render(request=request, template_name="index.html")

@login_required
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

@login_required
def election_list(request, format=None):
    if request.method == 'GET':
        elections = Election.objects.all()
        serialized_elections = None
        if elections:
            serializer = ElectionSerializer(instance=elections, many=True)
            serialized_elections = serializer.data
            
        return render(request=request, template_name="elections.html", context={"elections": serialized_elections})

@login_required
def election_details(request, pk, format=None):
    election = Election.get_element_by_id(id=pk)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes')
    
    if Election.check_voter_permission(id_election=pk, id_user=int(request.user.id))==False:
        messages.warning(request, 'Você não faz parte do grupo de eleitores desta eleição!')
        return redirect('eleicoes')
    
    if request.method == 'GET':
        serializer = ElectionSerializer(instance=election)
        #print(serializer.data)
        return render(request=request, template_name="election_details.html", context={"election": serializer.data})
    
@login_required            
def election_vote(request, pk, format=None):
    '''
    Funcion View para acesso à página de votação.
    GET para acessar formulário e POST para enviar o voto.
    '''
    id_election=pk
    id_user = int(request.user.id)
    election = Election.get_element_by_id(id=id_election)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes')

    if Election.check_voter_permission(id_election=pk, id_user=id_user)==False:
        messages.warning(request, 'Você não faz parte do grupo de eleitores desta eleição!')
        return redirect('eleicoes')
        
    if request.method == 'GET':
        serializer = ElectionSerializer(instance=election)
        election_voter = ElectionVoter.get_element(id_election=id_election, id_user=id_user)
        context = {
            "election": serializer.data,
            "voter_has_voted": election_voter.has_voted
        }
        return render(request=request, template_name="election_vote.html", context=context)
        
    if request.method == 'POST':
        #processar voto
        print(request.POST)
        serializer = ElectionSerializer(instance=election)
        return render(request=request, template_name="election_vote.html", context={"election": serializer.data})

#End-points extras
@api_view(['GET'])
def candidacy_details(request, pk, format=None):
    candidacy = Candidacy.get_element_by_id(id_candidacy=pk)
    print('requisição de candidatura recebida')
    if request.method == 'GET':
        if candidacy:
            print('enviando candidatura encontrada')
            serializer = CandidacySerializer(instance=candidacy)
            print('dados da candidatura encontrada')
            return Response(data=serializer.data)
            
        return Response(data='Not found.', status=status.HTTP_404_NOT_FOUND)
    
#End-points para teste