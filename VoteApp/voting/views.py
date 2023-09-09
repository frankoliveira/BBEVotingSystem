from django.shortcuts import render
from voting.forms import ElectionCreateForm
from django.contrib import messages

# Create your views here.
def criar_eleicao(request):
    if request.method == 'POST':
        election_form = ElectionCreateForm(request.POST)
        if election_form.is_valid():
            election = election_form.save(commit=False)
            election.author = request.user
            election.save()
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