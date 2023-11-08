#Model
from voting.models import Election, Candidacy, ElectionVoter
from security.models import PheManager

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
import uuid

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
            election.guid = uuid.uuid4()
            election.id_author = request.user
            election.creation = datetime.now()
            election.save()
            election.generate_phe_keys()
            
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
    
    if election.is_in_voting_period()==False:
        messages.warning(request, 'Não é possível votar fora do período de votação.')
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
        try:
            #print(request.POST)
            
            vote_is_valid = election.check_vote_validity(vote_form=request.POST)
            print("vote_is_valid: ", vote_is_valid)
            if vote_is_valid:
                id_transaction = election.process_vote(id_user=id_user, vote_form=request.POST)
                print("id_transaction: ", id_transaction)

            return redirect('eleicoes')
        except Exception as ex:
            messages.warning(request, 'Ocorreu um erro ao processar o voto.')
            return redirect('eleicoes')
    
#End-points extras
@api_view(['POST'])
def candidacy_details(request, format=None):
    '''
    End-point REST para obter dados da candidatura pelo número e eleição.
    '''
    print(request.data)
    if request.method == 'POST':
        try:
            id_election = int(request.data['id_election'])
            id_position = int(request.data['id_position'])
            number = int(request.data['number'])
            candidacy = Candidacy.get_element(id_election=id_election, id_position=id_position, number=number)
            if candidacy:
                serializer = CandidacySerializer(instance=candidacy)
                return Response(data=serializer.data)
            return Response(data='Not found.', status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response(data='Erro na requisição.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#End-points para teste