from rest_framework import serializers
from voting.models import Election, Question, Option, ElectionVoter

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'id_question', 'order', 'type', 'value', 'last_change']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True) #retorna o json das opções

    class Meta:
        model = Question
        fields = ['id', 'id_election', 'order', 'description', 'last_change', 'options']

class ElectionVoterIdUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectionVoter
        fields = ['id_user']

class ElectionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True) #retorna o json das questões
    #questions = serializers.PrimaryKeyRelatedField(many=True, queryset=Question.objects.all()) #retorna o id das questões
    #questions = serializers.PrimaryKeyRelatedField(many=True, read_only=True) #retorna o id das questões
    election_voters = ElectionVoterIdUserSerializer(many=True, read_only=True)
    

    class Meta:
        model = Election
        fields = ['id', 'id_author', 'tittle', 'description', 'creation', 'start', 'end', 'last_change', 'questions', 'election_voters']
