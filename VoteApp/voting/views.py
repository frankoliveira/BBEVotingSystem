#Model
from voting.models import Election

#Forms
from voting.forms import ElectionCreateForm

#Serializer
from voting.serializers import ElectionSerializer

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
def election_vote(request, pk, format=None):
    #if not request.user.is_authenticated:
    #    return redirect('login')

    election = Election.get_election_by_id(id_election=pk)

    if election==None:
        messages.warning(request, 'Eleição inexistente!')
        return redirect('eleicoes')

    if Election.check_voting_permission(id_election=pk, id_user=int(request.user.id))==False:
        messages.warning(request, 'Você não faz parte do grupo de eleitores da eleição!')
        return redirect('eleicoes')
        
    if request.method == 'GET':
        serializer = ElectionSerializer(instance=election)
        return render(request=request, template_name="election_vote.html", context={"election": serializer.data})
        
    if request.method == 'POST':
        #processar voto
        print(request.POST)
        serializer = ElectionSerializer(instance=election)
        return render(request=request, template_name="election_vote.html", context={"election": serializer.data})

