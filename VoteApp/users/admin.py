from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserCreateForm, CustomUserChangeForm
from users.models import CustomUser

@admin.register(CustomUser)
class CustomUsuarioAdmin(UserAdmin):
    add_form = CustomUserCreateForm #especifica o formulario usado na criação de usuário
    form = CustomUserChangeForm #especifica o formulario usado na atualização de usuário
    model = CustomUser #especifica o modelo a ser persistido no banco
    list_display = ('first_name', 'last_name', 'email', 'is_staff') #campos apresentados na tela de listagem
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
        ('Foto', {'fields': ('image',)})
    ) #