from rest_framework import serializers
from .models import Poll, Choice, Vote
from users.models import CustomUser


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'votes_count']


class PollListSerializer(serializers.ModelSerializer):
    """Serializer per lista sondaggi (senza scelte)"""
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'created_by',
            'created_at', 'total_votes', 'is_active', 'is_expired'
        ]


class PollDetailSerializer(serializers.ModelSerializer):
    """Serializer per dettaglio sondaggio (con scelte)"""
    choices = ChoiceSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'created_by',
            'created_at', 'updated_at', 'expires_at',
            'total_votes', 'is_active', 'is_expired', 'choices'
        ]


class PollCreateSerializer(serializers.ModelSerializer):
    """Serializer per creare sondaggi"""
    choices = serializers.ListField(
        child=serializers.CharField(max_length=200),
        min_length=2,
        max_length=10
    )

    class Meta:
        model = Poll
        fields = ['title', 'description', 'expires_at', 'choices']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        poll = Poll.objects.create(**validated_data)

        # Crea le scelte
        for choice_text in choices_data:
            Choice.objects.create(poll=poll, text=choice_text)

        return poll


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['choice', 'voted_at']

    def create(self, validated_data):
        # Aggiungi automaticamente user e poll
        choice = validated_data['choice']
        validated_data['poll'] = choice.poll
        validated_data['user'] = self.context['request'].user

        return super().create(validated_data)