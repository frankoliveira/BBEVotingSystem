from django.contrib.auth.forms import UserCreationForm, UserChangeForm #Formulários de criação e altualização
from users.models import CustomUser
from django.contrib.auth import urls
#print(f'URLs:{urls.urlpatterns}')

#Class Based View
class CustomUserCreateForm(UserCreationForm):
    #metadados
    class Meta:
        model = CustomUser #Especifica o modelo a ser persistido
        fields = ['username','first_name', 'last_name'] #Especifica os campos do modelo a serem
        labels = {'username': 'Username/E-mail'} #Especifica os labels dos campos no template

    def save(self, commit=True):
        user = super().save(commit=False) #recupera o usuário sem ainda inserir no banco
        #após o formulário ser submetido, acessamos os dados via cleaned_data
        user.set_password(self.cleaned_data["password1"]) #recupera do formulário o primeiro campo de senha
        user.email = self.cleaned_data["username"] #o email é usado no login
        if commit:
            user.save()
        return user

#alteração do cadastro
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser  # Especifica o modelo a ser persistido
        fields = ['first_name', 'last_name']  # Especifica os campos do modelo a serem preenchidos