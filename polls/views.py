from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Poll, Vote
from .permissions import IsOwnerOrReadOnly
from .serializers import PollListSerializer, PollDetailSerializer, PollCreateSerializer, VoteSerializer

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        import json
        data = json.loads(request.body)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Username e password obbligatori"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username già registrato"}, status=400)

        User.objects.create_user(username=username, password=password)
        return JsonResponse({"message": "Registrazione completata"}, status=201)



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
    queryset = Poll.objects.filter(is_active=True)
    serializer_class = PollDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]



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