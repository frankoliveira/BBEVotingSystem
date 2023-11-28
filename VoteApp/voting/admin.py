from django.contrib import admin
from voting.models import Election, Position, Candidacy, ElectionVoter, Vote, ElectionResult

# Register your models here.
@admin.register(Election)
class ElectionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'tittle') 

@admin.register(Position)
class PositionModelAdmin(admin.ModelAdmin):
    list_display = ('id_election', 'name')

@admin.register(Candidacy)
class CandidacyModelAdmin(admin.ModelAdmin):
    list_display = ('id_position', 'number', 'name')

@admin.register(ElectionVoter)
class ElectionVoterModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_election', 'id_user', 'has_voted')

@admin.register(Vote)
class VoteModelAdmin(admin.ModelAdmin):
    list_display = ('id_election', 'answer')