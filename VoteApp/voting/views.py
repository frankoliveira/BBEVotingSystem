#Model
from users.models import CustomUser
from voting.models import Election, Position, Candidacy, ElectionVoter, ElectionPhaseEnum
from security.PheManager import PheManager

#Forms
from voting.forms import ElectionCreateForm, ElectionUpdtateForm, PositionCreateForm, PositionUpdateForm
from voting.forms import CandidacyCreateForm
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
from django.core.paginator import Paginator

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
def election_list_manager(request, format=None):
    """
    Lista as eleições, ou cria uma nova.
    """

    if request.method == 'GET':
        election_list = Election.objects.all()
        paginator = Paginator(object_list=election_list, per_page=10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(request, "elections_manager.html", {"page_obj": page_obj})
    
    if request.method == 'POST':
        try:
            election_form = ElectionCreateForm(request.POST)
            if election_form.is_valid():
                election = election_form.save(commit=False)
                election.id_author = request.user
                election.save()
                return redirect('eleicao-gerenciador', pk=election.id)
            messages.error(request, "Erro ao criar eleição")
            return render(request=request, template_name="election_creation_manager.html", context={"election_form": election_form})
        except Exception as ex:
            print('POST election_creation_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('eleicoes-criacao-gerenciador')

def election_positions_list_manager(request, pk, format=None):
    id_eleicao = pk
    election = Election.get_element_by_id(id=id_eleicao)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes-gerenciador')

    if request.method == 'GET':
        try:
            positions = election.get_positions()
            context = {
                "election": election,
                "positions": positions
            }
            return render(request=request, template_name="election_positions_manager.html", context=context)
        except Exception as ex:
            print('GET election_positions_list_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro ao consultar cardos.')
            return redirect('eleicoes-gerenciador')
        
    if request.method == 'POST':
        try:
            #_position = Position()
            #_position.id_election = election
            #form = PositionCreateForm(request.POST, instance=_position)
            form = PositionCreateForm(request.POST)
            
            if form.is_valid():
                position = form.save(commit=False)
                #position.id_election = election
                position.save()
                return redirect('cargos-gerenciador', pk=election.id)
            print('erros no formulário do cargo: ', form.errors)
            messages.error(request, "Erro ao criar cargo")
            context={
                "election": election,
                "form": form
            }
            return render(request=request, template_name="position_creation_manager.html", context=context)
        except Exception as ex:
            print('POST election_creation_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('eleicoes-criacao-gerenciador')

def election_voters_list_manager(request, pk, format=None):
    id_eleicao = pk
    election = Election.get_element_by_id(id=id_eleicao)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes-gerenciador')
    
    if request.method == 'GET':
        voters_list = election.get_election_voters()
        paginator = Paginator(object_list=voters_list, per_page=10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {
            "election": election,
            "page_obj": page_obj
        }
        return render(request, "election_voters_list_manager.html", context=context)
    
    if request.method == 'POST':
        try:
            #para retornar à página de cadastro
            page_number = int(request.POST['page_number'])
            id_users_list = [int(id_user) for id_user in request.POST.getlist("id_users_list")]

            for id_user in id_users_list:
                user = CustomUser.objects.get(id=id_user)
                ElectionVoter.objects.create(id_election=election, id_user=user)

            return redirect(to=f'/gerenciador/eleicoes/{election.id}/eleitores/criacao/?page={page_number}')

        except Exception as ex:
            print('POST election_voters_list_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('eleitores-criacao-gerenciador', pk=election.id)

@login_required
def election_creation_manager(request):
    '''
    Página para criação de eleições.
    '''
    if request.method == 'GET':
        form = ElectionCreateForm()
        return render(request=request, template_name="election_creation_manager.html", context={"election_form": form})

def election_voter_creation_manager(request, pk, format=None):
    id_election = pk
    election = Election.get_element_by_id(id=id_election)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes-gerenciador')

    if request.method == 'GET':
        election_voters = ElectionVoter.objects.filter(id_election=id_election, excluded=False).select_related("id_user")
        election_voters_id_list = [voter.id_user.id for voter in election_voters]
        users_list = CustomUser.objects.all().order_by("first_name")
        paginator = Paginator(object_list=users_list, per_page=10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "election": election,
            "election_voters_id_list": election_voters_id_list,
            "page_obj": page_obj
        }
        return render(request, "election_voter_creation_manager.html", context=context)

def election_position_creation_manager(request, pk):
    '''
    Página para criação de cargo.
    '''
    id_eleicao = pk
    election = Election.get_element_by_id(id=id_eleicao)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes-gerenciador')
    
    if request.method == 'GET':
        form = PositionCreateForm()
        context = {
            "election": election,
            "election_form": form
        }
        return render(request=request, template_name="position_creation_manager.html", context=context)

@login_required
def election_update_manager(request, pk):
    '''
    Página para atualização de eleições.
    '''
    id_election=pk
    election = Election.get_element_by_id(id=id_election)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes-gerenciador')
    
    if request.method == 'GET':
        try:
            form = ElectionUpdtateForm(instance=election)
            context = {
                "election": election,
                "form": form
            }
            return render(request=request, template_name="election_update_manager.html", context=context) 
        except Exception as ex:
            print('GET election_update_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('eleicoes-gerenciador')

@login_required
def position_update_manager(request, pk):
    '''
    Página para atualização de cargo.
    '''
    id_position=pk
    position = Position.get_element_by_id(id=id_position)

    if position==None:
        messages.warning(request, 'Eleição ou Cargo inexistente!')
        return redirect('eleicoes-gerenciador')
    
    if request.method == 'GET':
        try:
            form = PositionUpdateForm(instance=position)
            context = {
                "election":  position.id_election,
                "id_position": id_position,
                "form": form
            }
            return render(request=request, template_name="position_update_manager.html", context=context) 
        except Exception as ex:
            print('GET position_update_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('eleicoes-gerenciador')

@login_required
def election_detail_manager(request, pk, format=None):
    '''
    Exibe ou atualiza uma eleição,
    '''
    id_election=pk
    election = Election.get_element_by_id(id=id_election)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes-gerenciador')
    
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
            return render(request=request, template_name="election_detail_manager.html", context=context)

        except Exception as ex:
            print('election_detail_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro ao consultar eleição.')
            return redirect('eleicoes-gerenciador')
    #Não consegui usar o PUT    
    if request.method == 'POST':
        try:
            form = ElectionUpdtateForm(data=request.POST, instance=election)
            if form.is_valid():
                form.save()
                return redirect('eleicao-gerenciador', pk=election.id)
            messages.warning(request, 'Erro ao atualizar.')
            return render(request=request, template_name="election_update_manager.html", context={"form": form})
        except Exception as ex:
            print('PUT election_update_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('eleicoes-gerenciador')

def position_detail_manager(request, pk, format=None):
    '''
    
    '''
    id_position=pk
    position = Position.get_element_by_id(id=id_position)

    if position==None:
        messages.warning(request, 'Cargo inexistente!')
        return redirect('eleicoes-gerenciador')
    
    #ATUALIZAR - seria o PUT mas não funfa no djang
    if request.method == 'POST':
        try:
            form = PositionUpdateForm(data=request.POST, instance=position)
            if form.is_valid():
                form.save()
                return redirect('cargos-gerenciador', pk=position.id_election.id)
            messages.warning(request, 'Erro ao atualizar cargo.')
            context={
                "form": form
            }
            return render(request=request, template_name="election_update_manager.html", context=context)
        except Exception as ex:
            print('POST election_position_detail_manager exception: ', ex)
            messages.warning(request, 'Ocorreu um erro.')
            return redirect('eleicoes-gerenciador')

def election_results_manager(request, pk, format=None):
    pass

@login_required
def election_vote_count(request, pk, format=None):
    '''
    Apuração de resultados da eleição.
    '''
    id_election=pk
    election = Election.get_element_by_id(id=id_election)

    #inserir lógica para apurar quando a eleição acabar

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes-gerenciador')
    
    if request.method == 'GET':
        try:
            election.vote_count()
            election.phase = ElectionPhaseEnum.PosVoting.value
            election.save()
            #não vai rediretionar para eleicoes-gerenciador
            return redirect('eleicoes-gerenciador')

        except Exception as ex:
            messages.warning(request, 'Ocorreu um erro ao apurar eleição.')
            return redirect('eleicoes-gerenciador')



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