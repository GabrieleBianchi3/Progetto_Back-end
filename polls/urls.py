from django.urls import path
from . import views

urlpatterns = [
    # API Endpoints
    path('', views.PollListCreateView.as_view(), name='poll-list-create'),
    path('<int:pk>/', views.PollDetailView.as_view(), name='poll-detail'),
    path('<int:poll_id>/vote/', views.vote_poll, name='poll-vote'),
    path('<int:poll_id>/results/', views.poll_results, name='poll-results'),
]