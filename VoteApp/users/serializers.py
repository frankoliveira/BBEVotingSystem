from rest_framework import serializers
from users.models import CustomUser

class VotePageCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'image']
        read_only_fields = ['first_name', 'last_name', 'image']