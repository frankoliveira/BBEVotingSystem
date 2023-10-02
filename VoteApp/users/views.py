from django.shortcuts import render, redirect
from users.forms import CustomUserCreateForm, CustomUserChangeForm
from django.contrib.auth import login
from django.contrib import messages

def sign_up(request):
    if request.method == 'GET':
        form = CustomUserCreateForm()
        return render(request=request, template_name="cadastro.html", context={"register_form": form}) 
    
    if request.method == 'POST':
        form = CustomUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registrado com sucesso")
            login(request, user)
            return redirect('index')
        return render(request=request, template_name="cadastro.html", context={"register_form": form})
