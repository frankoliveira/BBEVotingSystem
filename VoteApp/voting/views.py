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