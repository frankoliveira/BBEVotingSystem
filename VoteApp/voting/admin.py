from django.contrib import admin
from voting.models import Election, Question, Option, ElectionVoter, Vote, ElectionResult

# Register your models here.
@admin.register(Election)
class ElectionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'tittle') 

@admin.register(Question)
class QuestionModelAdmin(admin.ModelAdmin):
    list_display = ('id_election', 'description')

@admin.register(Option)
class OptionModelAdmin(admin.ModelAdmin):
    list_display = ('id_question', 'value')

@admin.register(ElectionVoter)
class ElectionVoterModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_election', 'id_user', 'has_voted')