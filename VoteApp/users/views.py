from django.shortcuts import render, redirect
from users.forms import CustomUserCreateForm
from django.contrib.auth import login
from django.contrib import messages

def sign_up(request):
    if request.method == 'POST':
        form = CustomUserCreateForm(request.POST)
        if form.is_valid():
            print(f"POST REQUEST: {request.POST}")
            user = form.save()
            login(request, user)
            messages.success(request, "Registrado com sucesso")
            return redirect('criar-eleicao')
        messages.error(request, "Erro ao registrar")

    form = CustomUserCreateForm()
    return render(request=request, template_name="register.html", context={"register_form": form})

def cadastrar(request):
    if request.method == 'POST':
        form = CustomUserCreateForm(request.POST)
        if form.is_valid():
            print(f"POST REQUEST: {request.POST}")
            user = form.save()
            login(request, user)
            messages.success(request, "Registrado com sucesso")
            return redirect('index')
        messages.error(request, "Erro ao registrar")
    form = CustomUserCreateForm()
    return render(request=request, template_name="cadastro.html", context={"register_form": form})