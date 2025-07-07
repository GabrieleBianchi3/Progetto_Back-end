from django.contrib import admin
from .models import Poll, Choice, Vote
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.admin import SimpleListFilter

class ExpiredFilter(SimpleListFilter):
    title = _('Is expired')
    parameter_name = 'is_expired'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(expiration_date__lt=timezone.now())
        if self.value() == 'no':
            return queryset.filter(expiration_date__gte=timezone.now())
        return queryset

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'expires_at')
    list_filter = ('expires_at', ExpiredFilter)



@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('poll', 'text', 'votes_count')
    list_filter = ('poll',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'choice', 'user', 'voted_at')
    list_filter = ('poll', 'user')


