from django.contrib import admin
from voting.models import Election, Question, Option, ElectionResult

# Register your models here.
@admin.register(Election)
class ElectionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_author', 'tittle') 

@admin.register(Question)
class QuestionModelAdmin(admin.ModelAdmin):
    list_display = ('id_election', 'description')

@admin.register(Option)
class OptionModelAdmin(admin.ModelAdmin):
    list_display = ('id_question', 'value')