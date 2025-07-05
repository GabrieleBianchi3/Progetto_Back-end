from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Poll, Choice, Vote
from .serializers import (
    PollListSerializer, PollDetailSerializer,
    PollCreateSerializer, VoteSerializer
)


class PollListCreateView(generics.ListCreateAPIView):
    """
    CLASS-BASED GENERIC VIEW (Requisito del progetto)
    GET: Lista tutti i sondaggi (anche per anonimi)
    POST: Crea nuovo sondaggio (solo autenticati)
    """
    queryset = Poll.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PollCreateSerializer
        return PollListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # Assegna automaticamente il creatore
        poll = serializer.save(created_by=self.request.user)
        # Aggiorna statistiche user
        self.request.user.polls_created += 1
        self.request.user.save()


class PollDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Dettaglio sondaggio con scelte (tutti)
    PUT/PATCH: Modifica sondaggio (solo creatore)
    DELETE: Elimina sondaggio (solo creatore)
    """
    queryset = Poll.objects.filter(is_active=True)
    serializer_class = PollDetailSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        poll = self.get_object()
        if poll.created_by != request.user:
            return Response(
                {'error': 'You can only edit your own polls'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        poll = self.get_object()
        if poll.created_by != request.user:
            return Response(
                {'error': 'You can only delete your own polls'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def vote_poll(request, poll_id):
    """
    Vota in un sondaggio
    Solo utenti autenticati
    """
    poll = get_object_or_404(Poll, id=poll_id, is_active=True)

    if poll.is_expired:
        return Response(
            {'error': 'This poll has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Controlla se ha già votato
    if Vote.objects.filter(user=request.user, poll=poll).exists():
        return Response(
            {'error': 'You have already voted in this poll'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = VoteSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        with transaction.atomic():
            vote = serializer.save()

            # Aggiorna contatori
            choice = vote.choice
            choice.votes_count += 1
            choice.save()

            poll.total_votes += 1
            poll.save()

            # Aggiorna statistiche user
            request.user.votes_cast += 1
            request.user.save()

        return Response(
            {'message': 'Vote recorded successfully'},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def poll_results(request, poll_id):
    """
    Risultati di un sondaggio
    Accessibile a tutti (anonimi + autenticati)
    """
    poll = get_object_or_404(Poll, id=poll_id, is_active=True)

    results = []
    for choice in poll.choices.all():
        percentage = 0
        if poll.total_votes > 0:
            percentage = round((choice.votes_count / poll.total_votes) * 100, 1)

        results.append({
            'choice': choice.text,
            'votes': choice.votes_count,
            'percentage': percentage
        })

    return Response({
        'poll': poll.title,
        'total_votes': poll.total_votes,
        'results': results
    })