from django.contrib import admin
from voting.models import Election

# Register your models here.
@admin.register(Election)
class SnippetModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'tittle') 