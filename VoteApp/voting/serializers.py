from rest_framework import serializers
from voting.models import Election, Position, Candidacy, ElectionVoter

class CandidacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidacy
        fields = ['id', 'id_election', 'id_position', 'number', 'name', 'description', 'type', 'value', 'last_change']

class PositionSerializer(serializers.ModelSerializer):
    candidacies = CandidacySerializer(many=True, read_only=True) #retorna o json das opções

    class Meta:
        model = Position
        fields = ['id', 'id_election', 'order', 'description', 'last_change', 'candidacies']

class ElectionVoterIdUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectionVoter
        fields = ['id_user']

class ElectionSerializer(serializers.ModelSerializer):
    positions = PositionSerializer(many=True, read_only=True) #retorna o json dos cargos
    #positions = serializers.PrimaryKeyRelatedField(many=True, queryset=Position.objects.all()) #retorna o id dos cargos
    #positions = serializers.PrimaryKeyRelatedField(many=True, read_only=True) #retorna o id dos cargos
    election_voters = ElectionVoterIdUserSerializer(many=True, read_only=True)

    class Meta:
        model = Election
        fields = ['id', 'id_author', 'tittle', 'description', 'creation', 'start', 'end', 'last_change', 'positions', 'election_voters']
