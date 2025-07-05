from django.db import models
from django.conf import settings
from django.utils import timezone


class Poll(models.Model):
    """
    Modello principale per i sondaggi
    RELAZIONE 1: User -> Poll (ForeignKey)
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_polls'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Statistiche
    total_votes = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        db_table = 'polls'

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class Choice(models.Model):
    """
    Opzioni di scelta per ogni sondaggio
    RELAZIONE 2: Poll -> Choice (ForeignKey)
    """
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField(max_length=200)
    votes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        db_table = 'choices'

    def __str__(self):
        return f"{self.poll.title} - {self.text}"


class Vote(models.Model):
    """
    Voti degli utenti
    RELAZIONI: User -> Vote, Choice -> Vote
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    voted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        # Un utente può votare solo una volta per sondaggio
        unique_together = ('user', 'poll')
        ordering = ['-voted_at']
        db_table = 'votes'

    def __str__(self):
        return f"{self.user.username} voted for {self.choice.text}"