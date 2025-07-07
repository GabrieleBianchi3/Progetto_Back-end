from django.urls import path
from . import views
from .views import RegisterView, poll_results


urlpatterns = [
    # Elenco e creazione di sondaggi
    path('polls/', views.PollListCreateView.as_view(), name='poll-list-create'),

    # Dettaglio di un singolo sondaggio
    path('polls/<int:pk>/', views.PollDetailView.as_view(), name='poll-detail'),

    # Votazione a un sondaggio specifico
    path('polls/<int:poll_id>/vote/', views.vote_poll, name='poll-vote'),

    # Registrazione utente
    path("register/", RegisterView.as_view(), name="register"),

    # Visualizzare i risulati
    path('polls/<int:poll_id>/results/', poll_results, name='poll-results'),

]
