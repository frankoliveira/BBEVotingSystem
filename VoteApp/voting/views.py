#Model
from voting.models import Election, Candidacy, ElectionVoter, ElectionPhaseEnum
from security.PheManager import PheManager

#Forms
from voting.forms import ElectionCreateForm, ElectionUpdtateForm

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

#************************ALL USERS****************************
@login_required
def index(request):
    if request.method == 'GET':
        return render(request=request, template_name="index.html")

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
        
    election_voter = ElectionVoter.get_element(id_election=id_election, id_user=id_user)

    if request.method == 'GET':
        serializer = ElectionSerializer(instance=election)
        context = {
            "election": serializer.data,
            "voter_has_voted": election_voter.has_voted,
        }
        return render(request=request, template_name="election_vote.html", context=context)
        
    if request.method == 'POST':
        try:
            vote_is_valid = election.check_vote_validity(vote_form=request.POST)
            '''serializer = ElectionSerializer(instance=election)
            context = {
                "election": serializer.data,
                "id_transaction": "a5caa89db5e862f28975d1785ba7cf63de43255609812e7d71ba471f07e613a6"
            }
            return render(request=request, template_name="election_vote_confirmation.html", context=context)'''
            
            if vote_is_valid:
                id_transaction = election.process_vote(id_user=id_user, vote_form=request.POST)
                serializer = ElectionSerializer(instance=election)
                if id_transaction:
                    context = {
                        "election": serializer.data,
                        "id_transaction": id_transaction
                    }
                    return render(request=request, template_name="election_vote_confirmation.html", context=context)
                messages.warning(request, 'Ocorreu um erro ao processar o voto.')
                return redirect('eleicoes')
            messages.warning(request, 'Voto inválido, não registrado.')
            return redirect('eleicoes')
        except Exception as ex:
            messages.warning(request, 'Ocorreu um erro ao processar o voto.')
            return redirect('eleicoes')

#************************ONLY ADMIN****************************
#Paginação de eleições
from django.core.paginator import Paginator
def election_list_manager(request, format=None):
    election_list = Election.objects.all()
    paginator = Paginator(object_list=election_list, per_page=10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "elections_manager.html", {"page_obj": page_obj})

@login_required
def election_creation_manager(request):
    if request.method == 'POST':
        try:
            election_form = ElectionCreateForm(request.POST)
            if election_form.is_valid():
                election = election_form.save(commit=False)
                election.id_author = request.user
                election.save()
                return redirect('detalhes-eleicao-gerenciador', pk=election.id)
            messages.error(request, "Erro ao criar eleição")
            return render(request=request, template_name="election_creation_manager.html", context={"election_form": election_form})
        except Exception as ex:
            print('POST election_creation_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('criar-eleicao')
        
    form = ElectionCreateForm()
    return render(request=request, template_name="election_creation_manager.html", context={"election_form": form})

@login_required
def election_update_manager(request, pk):
    id_election=pk
    election = Election.get_element_by_id(id=id_election)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('gerenciar-eleicoes')
    
    if request.method == 'GET':
        try:
            form = ElectionUpdtateForm(instance=election)
            return render(request=request, template_name="election_update_manager.html", context={"form": form}) 
        except Exception as ex:
            print('GET election_update_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('gerenciar-eleicoes')
        
    if request.method == 'POST':
        try:
            form = ElectionUpdtateForm(data=request.POST, instance=election)
            if form.is_valid():
                form.save()
                return redirect('detalhes-eleicao-gerenciador', pk=election.id)
            
            messages.warning(request, 'Erro ao atualizar.')
            return render(request=request, template_name="election_update_manager.html", context={"form": form})
        except Exception as ex:
            print('POST election_update_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('gerenciar-eleicoes')
        
@login_required
def election_details_manager(request, pk, format=None):
    id_election=pk
    election = Election.get_element_by_id(id=id_election)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('gerenciar-eleicoes')
    
    if request.method == 'GET':
        try:
            total_election_voters = len(election.get_election_voters())
            total_votes_received = election.get_total_votes_received()
            vote_count_allowed = election.voting_period_ended() and election.phase==2
            participation_percentage = round((total_votes_received/total_election_voters)*100, 2) if total_election_voters>0 else None

            context = {
                "election": election,
                "election_phase_description": ElectionPhaseEnum.get_description(value=election.phase),
                "total_election_voters": total_election_voters,
                "total_votes_received": total_votes_received,
                "vote_count_allowed": vote_count_allowed,
                "participation_percentage": participation_percentage
            }

            return render(request=request, template_name="election_details_manager.html", context=context)

        except Exception as ex:
            print('election_details_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro ao consultar eleição.')
            return redirect('gerenciar-eleicoes')
        
def election_results_manager(request, pk, format=None):
    pass

@login_required
def election_vote_count(request, pk, format=None):
    id_election=pk
    election = Election.get_element_by_id(id=id_election)

    #inserir lógica para apurar quando a eleição acabar

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('gerenciar-eleicoes')
    
    if request.method == 'GET':
        try:
            election.vote_count()
            election.phase = ElectionPhaseEnum.PosVoting.value
            election.save()
            #não vai rediretionar para gerenciar-eleicoes
            return redirect('gerenciar-eleicoes')

        except Exception as ex:
            messages.warning(request, 'Ocorreu um erro ao apurar eleição.')
            return redirect('gerenciar-eleicoes')

#End-points extras (REST)
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
                print(serializer.data)
                return Response(data=serializer.data)
            return Response(data='Not found.', status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response(data='Erro na requisição.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
def parcial_results(request, format=None):
    '''
    End-point REST para obter dados das candidaturas atuais.
    '''
    
    if request.method == 'POST':
        try:
            id_election = int(request.data['id_election'])
            print('ok')
            election = Election.get_element_by_id(id=id_election)
            result = election.election_parcial_count()
            return Response(data=result, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response(data='Erro na requisição.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
#End-points para teste